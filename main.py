"""
main.py — Точка входа для AEngine.

Создаёт экземпляр App и предоставляет ASGI-приложение для Hypercorn.
Использование:
    hypercorn main:asgi_app --bind 0.0.0.0:8000
    или для разработки: python main.py
"""

import os

from AEngineApps import App


def create_app() -> App:
    """Фабрика приложения AEngine с конфигурацией из переменных окружения."""
    debug = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")
    app_name = os.environ.get("APP_NAME", "AEngine")

    application = App(app_name=app_name, debug=debug)

    # Конфигурация из переменных окружения
    secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    application.flask.secret_key = secret_key

    # Базовая конфигурация приложения
    application.config = {
        "host": os.environ.get("HOST", "0.0.0.0"),
        "port": int(os.environ.get("PORT", "8000")),
        "debug": debug,
        "view": "web",  # Серверный режим (без webview)
    }

    # Health-check эндпоинт для Docker / балансировщиков
    @application.flask.route("/health")
    def health_check():
        return {"status": "healthy"}, 200

    application._register_default_error_handlers()

    return application


# Создаём экземпляр приложения
app = create_app()

# ASGI-приложение для Hypercorn через asgiref (Flask WSGI → ASGI адаптер)
# Hypercorn поддерживает WSGI-приложения напрямую через WsgiToAsgi
try:
    from asgiref.wsgi import WsgiToAsgi

    asgi_app = WsgiToAsgi(app.flask)
except ImportError:
    # Fallback: Hypercorn также может обслуживать WSGI напрямую
    asgi_app = app.flask


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    debug = os.environ.get("DEBUG", "true").lower() in ("true", "1", "yes")

    print(f"[AEngine] Запуск сервера разработки на http://{host}:{port}")
    app.flask.run(host=host, port=port, debug=debug)
