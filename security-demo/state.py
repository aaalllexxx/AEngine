"""
state.py — общее состояние демо-стенда поверх ``AEngineApps.GlobalStorage``.

Метрики и журнал событий хранятся в потокобезопасном singleton'е фреймворка
(`GlobalStorage`), как и рекомендует документация AEngineApps для обмена
состоянием между модулями без циклических импортов.
"""

import threading
import time

from AEngineApps import GlobalStorage

# Типы атак, по которым ведётся раздельная статистика (совпадают с UI).
ATTACK_TYPES = ["sqli", "xss", "lfi", "rce", "ddos", "cve", "dlp"]

# Ориентировочная «уверенность» детектора для наглядности (чисто UI-метрика).
SCORE_MAP = {"sqli": 95, "xss": 92, "lfi": 88, "rce": 95, "cve": 98, "dlp": 90, "ddos": 85}

_MAX_LOGS = 500

_lock = threading.Lock()
gs = GlobalStorage()


def _empty_metrics() -> dict:
    return {
        "total_attacks": 0,
        "blocked": 0,
        "passed": 0,
        "by_type": {t: {"blocked": 0, "passed": 0} for t in ATTACK_TYPES},
    }


def init_state() -> None:
    """Инициализирует хранилище метрик (идемпотентно)."""
    with _lock:
        if not gs.has("attack_logs"):
            gs.attack_logs = []
        if not gs.has("metrics"):
            gs.metrics = _empty_metrics()


def reset_metrics() -> None:
    """Полностью сбрасывает метрики и журнал."""
    with _lock:
        gs.attack_logs = []
        gs.metrics = _empty_metrics()


def log_attack(attack_type: str, blocked: bool, payload: str = "",
               detector: str = "", details: str = "") -> None:
    """Записывает событие атаки в GlobalStorage."""
    with _lock:
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": attack_type,
            "blocked": blocked,
            "payload": payload[:100],
            "detector": detector,
            "details": details,
            "ip": "127.0.0.1",
        }
        logs = gs.get("attack_logs", [])
        logs.append(entry)
        if len(logs) > _MAX_LOGS:
            logs = logs[-_MAX_LOGS:]
        gs.attack_logs = logs

        metrics = gs.get("metrics") or _empty_metrics()
        metrics["total_attacks"] += 1
        metrics["blocked" if blocked else "passed"] += 1
        if attack_type in metrics["by_type"]:
            metrics["by_type"][attack_type]["blocked" if blocked else "passed"] += 1
        gs.metrics = metrics


def get_metrics() -> dict:
    return gs.get("metrics") or _empty_metrics()


def get_logs(limit: int = 100) -> dict:
    logs = gs.get("attack_logs", [])
    return {"logs": logs[-limit:] if logs else [], "total": len(logs)}
