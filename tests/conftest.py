"""
conftest.py — Фикстуры pytest для проекта AEngine.

Предоставляет фикстуры для App, Screen, API, Service, GlobalStorage, JsonDict.
"""

import json
import os
import sys

import pytest

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from AEngineApps.app import App
from AEngineApps.api import API
from AEngineApps.global_storage import GlobalStorage
from AEngineApps.json_dict import JsonDict
from AEngineApps.screen import Screen
from AEngineApps.service import Service


# ─── App fixtures ──────────────────────────────────────────────


@pytest.fixture
def app():
    """Создаёт экземпляр App с минимальной конфигурацией."""
    application = App("TestApp", debug=True)
    application.flask.secret_key = "test-secret-key"
    application.config = {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": True,
        "view": "web",
    }
    return application


@pytest.fixture
def flask_app(app):
    """Возвращает Flask-приложение из App."""
    return app.flask


@pytest.fixture
def client(flask_app):
    """Создаёт Flask test client."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


# ─── Screen fixtures ──────────────────────────────────────────


@pytest.fixture
def sample_screen_cls():
    """Пример Screen-класса, возвращающего JSON."""

    class TestScreen(Screen):
        route = "/test"
        methods = ["GET"]

        def run(self):
            return self.json({"status": "ok"})

    return TestScreen


@pytest.fixture
def post_screen_cls():
    """Screen-класс, принимающий POST."""

    class PostScreen(Screen):
        route = "/submit"
        methods = ["GET", "POST"]

        def run(self):
            if self.request.method == "POST":
                return self.json({"received": True})
            return self.json({"method": "GET"})

    return PostScreen


# ─── API fixtures ──────────────────────────────────────────────


@pytest.fixture
def sample_api_cls():
    """Пример API-класса с GET и POST."""

    class TestAPI(API):
        route = "/api/test"
        methods = ["GET", "POST"]

        def get(self):
            return {"message": "hello"}

        def post(self):
            data = self.request.json or {}
            return {"echo": data}, 201

    return TestAPI


# ─── Service fixtures ─────────────────────────────────────────


@pytest.fixture
def sample_service(sample_api_cls):
    """Создаёт Service с зарегистрированным API."""
    svc = Service("test_service", prefix="/svc")
    svc.add_screen("/items", sample_api_cls)
    return svc


# ─── GlobalStorage fixtures ──────────────────────────────────


@pytest.fixture
def global_storage():
    """Создаёт GlobalStorage и очищает его после теста."""
    gs = GlobalStorage()
    gs.clear()
    yield gs
    gs.clear()
    # Сброс singleton для изоляции тестов
    GlobalStorage._instance = None
    GlobalStorage._data = {}


# ─── JsonDict fixtures ────────────────────────────────────────


@pytest.fixture
def json_file(tmp_path):
    """Создаёт временный JSON-файл с начальными данными."""
    filepath = tmp_path / "test_data.json"
    initial = {"name": "AEngine", "version": "1.0", "debug": False}
    filepath.write_text(json.dumps(initial, indent=2), encoding="utf-8")
    return str(filepath)


@pytest.fixture
def empty_json_file(tmp_path):
    """Создаёт пустой JSON-файл."""
    filepath = tmp_path / "empty.json"
    filepath.write_text("{}", encoding="utf-8")
    return str(filepath)


@pytest.fixture
def json_dict(json_file):
    """Создаёт JsonDict из временного файла."""
    return JsonDict(json_file)
