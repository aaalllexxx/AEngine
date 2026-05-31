"""
test_main.py — Тесты для точки входа main.py.

Проверяет create_app() и health-check эндпоинт /health.
"""

import os

import pytest


class TestCreateApp:
    """Тесты фабрики create_app()."""

    def test_create_app_returns_app(self):
        """create_app() возвращает объект App с Flask-приложением."""
        from main import create_app

        application = create_app()
        assert application is not None
        assert hasattr(application, "flask")
        assert application.flask is not None

    def test_create_app_name(self):
        """create_app() использует APP_NAME из env или дефолт."""
        from main import create_app

        app = create_app()
        # По умолчанию "AEngine"
        assert app.app_name == os.environ.get("APP_NAME", "AEngine")

    def test_create_app_has_config(self):
        """create_app() устанавливает базовую конфигурацию."""
        from main import create_app

        app = create_app()
        assert app.config.get("host") is not None
        assert app.config.get("port") is not None
        assert app.config.get("view") == "web"

    def test_create_app_secret_key(self):
        """create_app() устанавливает secret_key."""
        from main import create_app

        app = create_app()
        assert app.flask.secret_key is not None
        assert len(app.flask.secret_key) > 0


class TestHealthEndpoint:
    """Тесты health-check эндпоинта."""

    def test_health_check_returns_200(self):
        """GET /health возвращает 200."""
        from main import create_app

        app = create_app()
        app.flask.config["TESTING"] = True

        with app.flask.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200

    def test_health_check_json(self):
        """GET /health возвращает JSON со status: healthy."""
        from main import create_app

        app = create_app()
        app.flask.config["TESTING"] = True

        with app.flask.test_client() as client:
            response = client.get("/health")
            data = response.get_json()
            assert data is not None
            assert data["status"] == "healthy"

    def test_404_handler(self):
        """Несуществующий маршрут возвращает 404."""
        from main import create_app

        app = create_app()
        app.flask.config["TESTING"] = True

        with app.flask.test_client() as client:
            response = client.get("/this-route-does-not-exist")
            assert response.status_code == 404
