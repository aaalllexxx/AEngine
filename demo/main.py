"""
Демостенд AEngine: намеренно уязвимое приложение + модуль безопасности sec.

Запуск:
    python main.py

Дашборд безопасности: http://127.0.0.1:5057/sec-admin   (admin / admin)
На вкладке «Модули» можно включать/выключать защиту на лету.
Проверка уязвимостей: python attack_test.py
"""

import os
import sys

# Корень проекта в sys.path, чтобы работал авто-импорт screens/ и services/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AEngineApps.app import App
from AEngineApps.security import Security


class DemoApp(App):
    def __init__(self):
        super().__init__("AEngine Security Demo", debug=False)
        # Секрет нужен для сессий админ-дашборда.
        self.flask.secret_key = os.environ.get("DEMO_SECRET", "demo-secret-key")
        self.load_config(self.project_root + "config.json")


def build_app() -> DemoApp:
    """Создаёт приложение и подключает защиту (единая точка интеграции)."""
    app = DemoApp()
    Security(app).enable()
    return app


if __name__ == "__main__":
    build_app().run()
