"""
AEngineApps.security — единая точка интеграции модулей безопасности sec.

Подключает всю защиту к приложению одним вызовом и позволяет включать/выключать
модули на лету (в т.ч. из админ-дашборда). Состояние модулей хранится в
sec_modules.json в корне проекта.

Пример:
    from AEngineApps.app import App
    from AEngineApps.security import Security

    app = App("MyApp")
    app.load_config(app.project_root + "config.json")
    Security(app).enable()   # вся защита подключена
    app.run()
"""

import json
import os
import threading
from typing import Callable, Optional

from flask import abort

# Импорт модулей безопасности из того же пакета AEngineApps (куда их ставит `apm sec init`).
from AEngineApps.intrusions import IPS, IDS
from AEngineApps.os_protect import get_os_protection_module
from AEngineApps.net_analyzer import get_network_analyzer
from AEngineApps.sys_protect import AdvancedSystemProtection
from AEngineApps.logging import Logger


# Модули, которыми можно управлять из дашборда (имя -> описание).
MODULES_META = {
    "intrusion": "IDS/IPS: блокировка SQLi, XSS, RCE, LFI и сигнатур известных атак",
    "os_protect": "Защита ОС: контроль загрузки CPU/RAM (анти-DoS хоста)",
    "net_analyzer": "Анализ сети: SYN-flood, аномальные IP-соединения",
    "sys_protect": "Защита системы: сканер процессов, пользователей и конфигурации",
}
DEFAULT_ENABLED = {name: True for name in MODULES_META}

# Singleton — чтобы дашборд мог получить менеджер во время запроса.
_instance: "Optional[Security]" = None


def get_security() -> "Optional[Security]":
    """Возвращает текущий экземпляр Security (или None, если не инициализирован)."""
    return _instance


class Security:
    """Менеджер безопасности: подключает и переключает модули защиты приложения."""

    def __init__(self, app, config_path: Optional[str] = None, mode: str = "ips",
                 enable_logging: bool = True):
        global _instance
        self.app = app
        self.mode = mode  # "ips" — блокировать атаки, "ids" — только детектировать
        self.enable_logging = enable_logging
        self.config_path = config_path or os.path.join(app.project_root, "sec_modules.json")
        self._lock = threading.RLock()
        self.enabled = self._load_config()

        # Рантайм-экземпляры (создаются в enable()).
        self._ids = None
        self._os = None
        self._net = None
        self._sys = None
        self._logger = None

        _instance = self

    # ─── Конфигурация состояния модулей ───────────────────────

    def _load_config(self) -> dict:
        data = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                data = {}
        enabled = dict(DEFAULT_ENABLED)
        for name, value in (data or {}).items():
            if name in enabled:
                enabled[name] = bool(value)
        return enabled

    def _save_config(self) -> None:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.enabled, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def is_enabled(self, name: str) -> bool:
        return bool(self.enabled.get(name, False))

    def set_enabled(self, name: str, value: bool) -> bool:
        """Включает/выключает модуль на лету и сохраняет состояние. Возвращает новое значение."""
        if name not in MODULES_META:
            raise KeyError(name)
        with self._lock:
            self.enabled[name] = bool(value)
            self._save_config()
        return self.enabled[name]

    def list_modules(self) -> list:
        """Список модулей для дашборда: имя, описание, состояние."""
        return [
            {"name": name, "description": MODULES_META[name], "enabled": self.is_enabled(name)}
            for name in MODULES_META
        ]

    # ─── Доступ к рантайм-инструментам (для дашборда) ──────────

    @property
    def os_protection(self):
        if self._os is None:
            self._os = get_os_protection_module()
        return self._os

    @property
    def net_analyzer(self):
        if self._net is None:
            self._net = get_network_analyzer()
        return self._net

    @property
    def sys_protection(self):
        if self._sys is None:
            self._sys = AdvancedSystemProtection(scan_interval=0, auto_start=False)
        return self._sys

    # ─── Подключение к приложению ─────────────────────────────

    def enable(self) -> "Security":
        """Подключает всю защиту к приложению согласно конфигу (с возможностью live-переключения)."""
        # Логирование — фундамент (пишет logs/app.log, нужно для журнала инцидентов в дашборде).
        if self.enable_logging:
            try:
                self._logger = Logger(self.app)
            except Exception as e:
                print(f"[Security] Не удалось инициализировать логирование: {e}")

        # IDS/IPS: один хук, который сам проверяет, включён ли модуль intrusion.
        detector_system = IPS if self.mode == "ips" else IDS
        self._ids = detector_system(self.app, is_enabled=lambda: self.is_enabled("intrusion"))

        # Лёгкий per-request guard для анти-DoS ОС (если включён). Тяжёлые сетевые/системные
        # сканы выполняются по запросу из дашборда, а не на каждый HTTP-запрос.
        self.app.flask.before_request(self._guard)

        print("[Security] Модули безопасности подключены: "
              + ", ".join(f"{n}={'on' if self.is_enabled(n) else 'off'}" for n in MODULES_META))
        return self

    def _guard(self) -> None:
        if self.is_enabled("os_protect"):
            try:
                res = self.os_protection.check_resources()
                if res.get("status") == "danger":
                    self.app.flask.logger.critical(
                        f"[OS Protect] Перегрузка ОС: {res.get('warnings')}")
                    abort(503, description="Service Unavailable: High Server Load")
            except Exception:
                pass

    @property
    def ids(self):
        """IDS/IPS-экземпляр (для добавления пользовательских правил/детекторов)."""
        return self._ids
