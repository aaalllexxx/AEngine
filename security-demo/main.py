"""
AEngine Security Demo — точка входа.

Стенд построен по структуре AEngineApps (`App` + `config.json` + экраны
`Screen`/`API` + `GlobalStorage`) и использует модуль ``sec`` строго по
документации: компоненты IPS / DLP / RateLimiter привязываются к приложению, а
полезные нагрузки прогоняются НАСТОЯЩИМИ запросами через защищённое приложение
(см. ``sandbox.py``). Логика защиты в стенде не дублируется.
"""

import os
import sys

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(DEMO_DIR)

# AEngineApps / sec лежат в корне репозитория; screens / sandbox / state — рядом.
for _path in (REPO_ROOT, DEMO_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)


# ─── Авто-установка зависимостей (bootstrap) ───────────────────
#
# При прямом запуске (``python main.py``) стенд сам доустанавливает недостающие
# Python-зависимости из ``requirements.txt`` — чтобы свежий клон поднимался
# «из коробки». ``AEngineApps`` импортирует ``webview`` на уровне модуля, а ``sec``
# тянет ``rich``, поэтому оба пакета нужны даже в web-режиме стенда.
#
# Отключается переменной окружения ``AENGINE_NO_AUTO_INSTALL=1`` — например, в
# Docker, где зависимости уже установлены на этапе сборки образа.

def _ensure_dependencies() -> None:
    """Доустанавливает отсутствующие зависимости из ``requirements.txt``."""
    import importlib.util

    # модуль для импорта → имя дистрибутива на PyPI
    required = {
        "flask": "flask",
        "psutil": "psutil",
        "webview": "pywebview",  # AEngineApps импортирует webview на уровне модуля
        "rich": "rich",          # sec тянет rich при импорте (sec/logging.py)
    }
    missing = [pkg for mod, pkg in required.items() if importlib.util.find_spec(mod) is None]
    if not missing:
        return

    pretty = ", ".join(missing)
    req_file = os.path.join(DEMO_DIR, "requirements.txt")

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


from AEngineApps import App

from state import init_state
from screens.pages import IndexPage, HealthScreen
from screens.attacks import (
    AttacksCatalogAPI, AttackRunAPI, AttackFloodAPI, DLPTestAPI, AttackChainAPI,
)
from screens.metrics import (
    MetricsSummaryAPI, MetricsSystemAPI, MetricsLogsAPI, StressTestAPI, MetricsResetAPI,
)

# Все экраны стенда (регистрируются явно — документированный способ AEngineApps).
SCREENS = {
    IndexPage.route: IndexPage,
    HealthScreen.route: HealthScreen,
    AttacksCatalogAPI.route: AttacksCatalogAPI,
    AttackRunAPI.route: AttackRunAPI,
    AttackFloodAPI.route: AttackFloodAPI,
    DLPTestAPI.route: DLPTestAPI,
    AttackChainAPI.route: AttackChainAPI,
    MetricsSummaryAPI.route: MetricsSummaryAPI,
    MetricsSystemAPI.route: MetricsSystemAPI,
    MetricsLogsAPI.route: MetricsLogsAPI,
    StressTestAPI.route: StressTestAPI,
    MetricsResetAPI.route: MetricsResetAPI,
}


def _truthy(value: str) -> bool:
    return value.lower() in ("1", "true", "yes")


def create_app() -> App:
    """Собирает приложение стенда по структуре AEngineApps."""
    app = App("SecurityDemo")

    # Стенд живёт в подкаталоге репозитория → static/templates/экраны берём отсюда.
    app.project_root = DEMO_DIR + os.sep
    app.flask.root_path = DEMO_DIR
    app.flask.secret_key = os.environ.get("SECRET_KEY", "security-demo-secret-key")

    app.load_config(os.path.join(DEMO_DIR, "config.json"))

    # Переопределение конфигурации через переменные окружения.
    if os.environ.get("HOST"):
        app.config["host"] = os.environ["HOST"]
    if os.environ.get("PORT"):
        app.config["port"] = int(os.environ["PORT"])
    if os.environ.get("DEBUG"):
        app.config["debug"] = _truthy(os.environ["DEBUG"])

    init_state()
    app.add_screens(SCREENS)
    return app


app = create_app()


if __name__ == "__main__":
    port = app.config.get("port", 5050)
    print("=" * 60)
    print("  AEngine Security Demo")
    print(f"  http://127.0.0.1:{port}")
    print("  Использует реальный модуль sec (IPS/IDS, RateLimiter, DLP)")
    print("=" * 60)
    app.run()
