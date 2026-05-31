"""
test_app.py — Тесты для всех компонентов AEngineApps.

Покрывает: App, Screen, API, Service, GlobalStorage, JsonDict.
"""

import json
import threading

import pytest

from AEngineApps.app import App
from AEngineApps.api import API
from AEngineApps.global_storage import GlobalStorage
from AEngineApps.json_dict import JsonDict
from AEngineApps.screen import Screen
from AEngineApps.service import Service


# ═══════════════════════════════════════════════════════════════
# App
# ═══════════════════════════════════════════════════════════════


class TestAppCreation:
    """Тесты создания и конфигурации App."""

    def test_app_creation_default(self):
        """App создаётся с именем по умолчанию."""
        application = App()
        assert application.flask is not None
        assert application.flask.debug is False

    def test_app_creation_with_name(self):
        """App создаётся с указанным именем."""
        application = App("MyApp", debug=True)
        assert application.app_name == "MyApp"
        assert application.flask.debug is True

    def test_app_has_flask_instance(self, app):
        """App содержит Flask-экземпляр."""
        assert app.flask is not None
        assert app.app_name == "TestApp"

    def test_app_config_setter(self, app):
        """config setter корректно устанавливает значения."""
        app.config = {"host": "0.0.0.0", "port": 9000}
        assert app.config["host"] == "0.0.0.0"
        assert app.config["port"] == 9000

    def test_app_config_preserves_existing(self, app):
        """Повторная установка config не теряет старые ключи."""
        app.config = {"host": "127.0.0.1", "port": 5000}
        app.config = {"custom_key": "value"}
        assert app.config.get("host") == "127.0.0.1"
        assert app.config.get("custom_key") == "value"


class TestAppScreenRouting:
    """Тесты регистрации Screen в App."""

    def test_add_screen(self, app, sample_screen_cls, client):
        """add_screen регистрирует Screen по пути."""
        app.add_screen("/test", sample_screen_cls)
        response = client.get("/test")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"

    def test_add_screens_batch(self, app, sample_screen_cls, client):
        """add_screens регистрирует несколько Screen."""

        class AnotherScreen(Screen):
            methods = ["GET"]

            def run(self):
                return self.json({"page": "another"})

        app.add_screens({"/test": sample_screen_cls, "/another": AnotherScreen})

        r1 = client.get("/test")
        assert r1.status_code == 200
        assert r1.get_json()["status"] == "ok"

        r2 = client.get("/another")
        assert r2.status_code == 200
        assert r2.get_json()["page"] == "another"

    def test_add_router_function(self, app, client):
        """add_router регистрирует обычную функцию как роут."""

        def hello():
            return "hello world"

        app.add_router("/hello", hello)
        response = client.get("/hello")
        assert response.status_code == 200
        assert response.data == b"hello world"

    def test_add_routers_batch(self, app, client):
        """add_routers регистрирует несколько функций."""

        def func_a():
            return "A"

        def func_b():
            return "B"

        app.add_routers({"/a": func_a, "/b": func_b})
        assert client.get("/a").data == b"A"
        assert client.get("/b").data == b"B"


class TestAppHooks:
    """Тесты on_start/on_stop хуков."""

    def test_on_start_hook(self, app):
        """on_start добавляет хук в список."""
        called = []
        app.on_start(lambda: called.append("started"))
        assert len(app._startup_hooks) == 1
        app._run_hooks(app._startup_hooks)
        assert called == ["started"]

    def test_on_stop_hook(self, app):
        """on_stop добавляет хук в список."""
        called = []
        app.on_stop(lambda: called.append("stopped"))
        assert len(app._shutdown_hooks) == 1
        app._run_hooks(app._shutdown_hooks)
        assert called == ["stopped"]

    def test_hook_exception_does_not_propagate(self, app):
        """Исключение в хуке не прерывает выполнение остальных."""
        results = []

        def bad_hook():
            raise RuntimeError("boom")

        def good_hook():
            results.append("ok")

        app.on_start(bad_hook)
        app.on_start(good_hook)
        app._run_hooks(app._startup_hooks)
        assert results == ["ok"]


class TestAppMiddleware:
    """Тесты before_request / after_request."""

    def test_before_request(self, app, sample_screen_cls, client):
        """before_request перехватывает запрос."""
        intercepted = []

        def middleware():
            intercepted.append(True)

        app.before_request(middleware)
        app.add_screen("/test", sample_screen_cls)

        client.get("/test")
        assert len(intercepted) == 1

    def test_after_request(self, app, sample_screen_cls, client):
        """after_request вызывается после обработки запроса."""
        headers_added = []

        def add_header(response):
            response.headers["X-Custom"] = "test"
            headers_added.append(True)
            return response

        app.after_request(add_header)
        app.add_screen("/test", sample_screen_cls)

        response = client.get("/test")
        assert response.headers.get("X-Custom") == "test"
        assert len(headers_added) == 1


class TestAppErrorHandlers:
    """Тесты error handler'ов."""

    def test_default_404(self, app, client):
        """Дефолтный 404 handler возвращает HTML с кодом 404."""
        app._register_default_error_handlers()
        response = client.get("/nonexistent-route")
        assert response.status_code == 404
        assert b"404" in response.data


# ═══════════════════════════════════════════════════════════════
# Screen
# ═══════════════════════════════════════════════════════════════


class TestScreen:
    """Тесты базового класса Screen."""

    def test_screen_defaults(self):
        """Screen имеет дефолтные route и methods."""
        s = Screen()
        assert s.route == "/"
        assert s.methods == ["GET"]

    def test_screen_run_raises_not_implemented(self):
        """run() базового Screen бросает NotImplementedError."""
        s = Screen()
        with pytest.raises(NotImplementedError):
            s.run()

    def test_screen_callable(self):
        """Screen вызывается как функция (__call__ → run)."""
        s = Screen()
        with pytest.raises(NotImplementedError):
            s()

    def test_screen_json_response(self, app, client):
        """Screen.json() возвращает JSON-ответ."""

        class JsonScreen(Screen):
            methods = ["GET"]

            def run(self):
                return self.json({"key": "value"}, 200)

        app.add_screen("/json", JsonScreen)
        response = client.get("/json")
        assert response.status_code == 200
        assert response.get_json() == {"key": "value"}

    def test_screen_json_custom_status(self, app, client):
        """Screen.json() поддерживает кастомный статус-код."""

        class StatusScreen(Screen):
            methods = ["GET"]

            def run(self):
                return self.json({"error": "not found"}, 404)

        app.add_screen("/status", StatusScreen)
        response = client.get("/status")
        assert response.status_code == 404

    def test_screen_redirect(self, app, client):
        """Screen.redirect() перенаправляет на указанный URL."""

        class RedirectScreen(Screen):
            methods = ["GET"]

            def run(self):
                return self.redirect("/target")

        app.add_screen("/redir", RedirectScreen)
        response = client.get("/redir")
        assert response.status_code == 302
        assert "/target" in response.headers.get("Location", "")

    def test_screen_post_method(self, app, post_screen_cls, client):
        """Screen обрабатывает POST-запросы."""
        app.add_screen("/submit", post_screen_cls)

        get_resp = client.get("/submit")
        assert get_resp.get_json()["method"] == "GET"

        post_resp = client.post("/submit")
        assert post_resp.get_json()["received"] is True

    def test_screen_abort(self, app, client):
        """Screen.abort() прерывает запрос с кодом ошибки."""

        class AbortScreen(Screen):
            methods = ["GET"]

            def run(self):
                self.abort(403)

        app.add_screen("/forbidden", AbortScreen)
        response = client.get("/forbidden")
        assert response.status_code == 403

    def test_screen_client_ip(self, app, client):
        """Screen.client_ip возвращает IP клиента."""
        ip_result = {}

        class IPScreen(Screen):
            methods = ["GET"]

            def run(self):
                ip_result["ip"] = self.client_ip
                return self.json({"ip": self.client_ip})

        app.add_screen("/ip", IPScreen)
        client.get("/ip")
        assert ip_result["ip"] == "127.0.0.1"

    def test_screen_client_ip_forwarded(self, app, client):
        """Screen.client_ip учитывает X-Forwarded-For."""
        ip_result = {}

        class IPScreen(Screen):
            methods = ["GET"]

            def run(self):
                ip_result["ip"] = self.client_ip
                return self.json({"ip": self.client_ip})

        app.add_screen("/ip2", IPScreen)
        client.get("/ip2", headers={"X-Forwarded-For": "10.0.0.1, 192.168.1.1"})
        assert ip_result["ip"] == "10.0.0.1"


# ═══════════════════════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════════════════════


class TestAPI:
    """Тесты для API-класса (подкласс Screen)."""

    def test_api_get(self, app, sample_api_cls, client):
        """API.get() вызывается при GET-запросе."""
        app.add_screen("/api/test", sample_api_cls)
        response = client.get("/api/test")
        assert response.status_code == 200
        assert response.get_json()["message"] == "hello"

    def test_api_post(self, app, sample_api_cls, client):
        """API.post() вызывается при POST-запросе и возвращает 201."""
        app.add_screen("/api/test", sample_api_cls)
        response = client.post(
            "/api/test",
            data=json.dumps({"key": "value"}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["echo"] == {"key": "value"}

    def test_api_method_not_allowed(self, app, client):
        """API без put() возвращает 405 при PUT-запросе."""

        class LimitedAPI(API):
            methods = ["GET", "PUT"]

            def get(self):
                return {"ok": True}

        app.add_screen("/api/limited", LimitedAPI)
        response = client.put("/api/limited")
        assert response.status_code == 405
        assert response.get_json()["error"] == "Method Not Allowed"

    def test_api_auto_json_list(self, app, client):
        """API автоматически конвертирует list в JSON."""

        class ListAPI(API):
            methods = ["GET"]

            def get(self):
                return [1, 2, 3]

        app.add_screen("/api/list", ListAPI)
        response = client.get("/api/list")
        assert response.status_code == 200
        assert response.get_json() == [1, 2, 3]

    def test_api_get_arg(self, app, client):
        """API.get_arg() извлекает query-параметры с типизацией."""

        class ArgAPI(API):
            methods = ["GET"]

            def get(self):
                limit = self.get_arg("limit", type_func=int, default=10)
                return {"limit": limit}

        app.add_screen("/api/args", ArgAPI)

        r1 = client.get("/api/args?limit=25")
        assert r1.get_json()["limit"] == 25

        r2 = client.get("/api/args")
        assert r2.get_json()["limit"] == 10

        r3 = client.get("/api/args?limit=abc")
        assert r3.get_json()["limit"] == 10

    def test_api_require_keys(self, app, client):
        """API.require_keys() проверяет обязательные ключи в JSON."""

        class ValidAPI(API):
            methods = ["POST"]

            def post(self):
                ok, missing = self.require_keys(["username", "password"])
                if not ok:
                    return {"error": f"Missing: {missing}"}, 400
                return {"status": "ok"}

        app.add_screen("/api/validate", ValidAPI)

        # Полный payload
        r1 = client.post(
            "/api/validate",
            data=json.dumps({"username": "admin", "password": "123"}),
            content_type="application/json",
        )
        assert r1.status_code == 200

        # Отсутствует password
        r2 = client.post(
            "/api/validate",
            data=json.dumps({"username": "admin"}),
            content_type="application/json",
        )
        assert r2.status_code == 400
        assert "password" in r2.get_json()["error"]


# ═══════════════════════════════════════════════════════════════
# Service
# ═══════════════════════════════════════════════════════════════


class TestService:
    """Тесты для Service (Blueprint-обёртка)."""

    def test_service_creation(self):
        """Service создаётся с именем и префиксом."""
        svc = Service("auth", prefix="/auth")
        assert svc.name == "auth"
        assert svc.prefix == "/auth"
        assert svc.blueprint is not None

    def test_service_add_screen(self):
        """Service.add_screen() регистрирует Screen в blueprint."""

        class SvcScreen(Screen):
            methods = ["GET"]

            def run(self):
                return self.json({"svc": True})

        svc = Service("test_svc", prefix="/s")
        svc.add_screen("/page", SvcScreen)
        assert len(svc._screens) == 1

    def test_service_registration_in_app(self, app, client):
        """register_service() делает Screen сервиса доступным по URL."""

        class ItemAPI(API):
            methods = ["GET"]

            def get(self):
                return {"items": []}

        svc = Service("items_svc", prefix="/api/v1")
        svc.add_screen("/items", ItemAPI)
        app.register_service(svc)

        response = client.get("/api/v1/items")
        assert response.status_code == 200
        assert response.get_json()["items"] == []

    def test_service_before_request(self, app, client):
        """Service.before_request() работает как middleware для сервиса."""
        intercepted = []

        class SvcScreen(Screen):
            methods = ["GET"]

            def run(self):
                return self.json({"ok": True})

        svc = Service("middleware_svc", prefix="/mid")
        svc.add_screen("/check", SvcScreen)
        svc.before_request(lambda: intercepted.append(True))
        app.register_service(svc)

        client.get("/mid/check")
        assert len(intercepted) == 1


# ═══════════════════════════════════════════════════════════════
# GlobalStorage
# ═══════════════════════════════════════════════════════════════


class TestGlobalStorage:
    """Тесты для GlobalStorage (thread-safe singleton)."""

    def test_singleton(self, global_storage):
        """Все экземпляры GlobalStorage — один объект."""
        gs1 = GlobalStorage()
        gs2 = GlobalStorage()
        assert gs1 is gs2

    def test_set_and_get(self, global_storage):
        """Установка и чтение атрибутов."""
        global_storage.username = "admin"
        assert global_storage.username == "admin"

    def test_get_with_default(self, global_storage):
        """get() возвращает default для отсутствующих ключей."""
        assert global_storage.get("nonexistent") is None
        assert global_storage.get("nonexistent", 42) == 42

    def test_has(self, global_storage):
        """has() проверяет наличие ключа."""
        assert global_storage.has("x") is False
        global_storage.x = 1
        assert global_storage.has("x") is True

    def test_delete(self, global_storage):
        """delete() удаляет ключ."""
        global_storage.temp = "value"
        assert global_storage.has("temp") is True
        global_storage.delete("temp")
        assert global_storage.has("temp") is False

    def test_clear(self, global_storage):
        """clear() очищает всё хранилище."""
        global_storage.a = 1
        global_storage.b = 2
        global_storage.clear()
        assert global_storage.all() == {}

    def test_all(self, global_storage):
        """all() возвращает копию всех данных."""
        global_storage.x = 10
        global_storage.y = 20
        data = global_storage.all()
        assert data == {"x": 10, "y": 20}
        # Проверяем, что это копия
        data["z"] = 30
        assert global_storage.has("z") is False

    def test_attribute_error_on_missing(self, global_storage):
        """Доступ к несуществующему атрибуту бросает AttributeError."""
        with pytest.raises(AttributeError, match="GlobalStorage не содержит"):
            _ = global_storage.missing_key

    def test_repr(self, global_storage):
        """__repr__ возвращает строковое представление."""
        global_storage.key = "val"
        r = repr(global_storage)
        assert "GlobalStorage" in r
        assert "key" in r

    def test_thread_safety(self, global_storage):
        """Параллельная запись из нескольких потоков не вызывает ошибок."""
        errors = []

        def writer(key, value):
            try:
                setattr(global_storage, key, value)
                assert getattr(global_storage, key) is not None
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=writer, args=(f"key_{i}", i))
            for i in range(20)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(global_storage.all()) == 20

    def test_shared_state_across_instances(self, global_storage):
        """Разные экземпляры видят одни и те же данные."""
        gs1 = GlobalStorage()
        gs2 = GlobalStorage()
        gs1.shared = "data"
        assert gs2.shared == "data"


# ═══════════════════════════════════════════════════════════════
# JsonDict
# ═══════════════════════════════════════════════════════════════


class TestJsonDict:
    """Тесты для JsonDict (JSON файл как dict)."""

    def test_load_existing(self, json_dict):
        """JsonDict загружает данные из файла."""
        assert json_dict["name"] == "AEngine"
        assert json_dict["version"] == "1.0"
        assert json_dict["debug"] is False

    def test_load_nonexistent_file(self, tmp_path):
        """JsonDict с несуществующим файлом создаёт пустой словарь."""
        jd = JsonDict(str(tmp_path / "nonexistent.json"))
        assert jd.dictionary == {}

    def test_get_attribute(self, json_dict):
        """Доступ к атрибуту через точку."""
        assert json_dict.name == "AEngine"

    def test_set_attribute_auto_save(self, json_dict, json_file):
        """Установка атрибута автоматически сохраняет в файл."""
        json_dict.new_key = "new_value"
        assert json_dict.new_key == "new_value"

        # Проверяем, что данные записаны в файл
        with open(json_file, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["new_key"] == "new_value"

    def test_get_item(self, json_dict):
        """Доступ через [] (dict-like)."""
        assert json_dict["name"] == "AEngine"

    def test_set_item(self, json_dict, json_file):
        """Установка через [] автосохраняет."""
        json_dict["new_item"] = 42
        assert json_dict["new_item"] == 42

        with open(json_file, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["new_item"] == 42

    def test_get_with_default(self, json_dict):
        """get() с default для отсутствующих ключей."""
        assert json_dict.get("missing") is None
        assert json_dict.get("missing", "fallback") == "fallback"

    def test_has(self, json_dict):
        """has() проверяет наличие ключа."""
        assert json_dict.has("name") is True
        assert json_dict.has("nonexistent") is False

    def test_contains(self, json_dict):
        """Поддержка оператора `in`."""
        assert "name" in json_dict
        assert "nonexistent" not in json_dict

    def test_keys_values_items(self, json_dict):
        """keys(), values(), items() работают корректно."""
        assert "name" in json_dict.keys()
        assert "AEngine" in json_dict.values()
        assert ("name", "AEngine") in json_dict.items()

    def test_delete_item(self, json_dict, json_file):
        """delete_item() удаляет ключ и сохраняет файл."""
        json_dict.delete_item("debug")
        assert "debug" not in json_dict
        assert json_dict.get("debug") is None

        with open(json_file, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert "debug" not in saved

    def test_update(self, json_dict, json_file):
        """update() обновляет несколько ключей и сохраняет."""
        json_dict.update({"host": "localhost", "port": 8080})
        assert json_dict["host"] == "localhost"
        assert json_dict["port"] == 8080

        with open(json_file, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["host"] == "localhost"

    def test_save(self, json_dict, json_file):
        """save() принудительно сохраняет на диск."""
        json_dict.dictionary["manual"] = True
        json_dict.save()

        with open(json_file, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["manual"] is True

    def test_batch_update(self, json_dict, json_file):
        """batch_update() откладывает запись до выхода из context manager."""
        with json_dict.batch_update():
            json_dict.batch_a = 1
            json_dict.batch_b = 2
            json_dict.batch_c = 3

        with open(json_file, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["batch_a"] == 1
        assert saved["batch_b"] == 2
        assert saved["batch_c"] == 3

    def test_repr(self, json_dict):
        """__repr__ возвращает JSON-строку."""
        r = repr(json_dict)
        assert "AEngine" in r
        # Проверяем, что это валидный JSON
        parsed = json.loads(r)
        assert parsed["name"] == "AEngine"

    def test_empty_file(self, empty_json_file):
        """JsonDict корректно загружает пустой JSON-файл."""
        jd = JsonDict(empty_json_file)
        assert jd.dictionary == {}
