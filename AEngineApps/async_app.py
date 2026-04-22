"""
AsyncApp -- asynchronous AEngine application based on Quart.
"""

from __future__ import annotations

import inspect
import os
import socket
from importlib import import_module
from typing import Any, Callable, Optional

from quart import Quart, Response, make_response

from AEngineApps.async_screen import AsyncScreen
from AEngineApps.json_dict import JsonDict


class AsyncApp:
    """Async version of App using Quart."""

    def __init__(self, app_name: str = __name__, debug: bool = False):
        self.app_name = app_name
        self.project_root = os.path.dirname(os.path.dirname(__file__)) + os.sep
        self.quart: Quart = Quart(
            self.app_name,
            static_folder=os.path.join(self.project_root, "static"),
            template_folder=os.path.join(self.project_root, "templates"),
        )
        self.quart.debug = debug
        self.quart.root_path = self.project_root
        self.__config: dict[str, Any] = {}
        self._startup_hooks: list[Callable] = []
        self._shutdown_hooks: list[Callable] = []
        self._request_count = 0
        self._health_enabled = False
        self._metrics_enabled = False
        self._metrics_registered = False

        @self.quart.before_request
        async def _track_requests():
            self._request_count += 1

    def add_screen(self, path: str, screen_cls: type, **options) -> None:
        instance = screen_cls()
        instance._app = self
        instance.__name__ = path.replace("/", "_") or "_root"

        if "methods" not in options and hasattr(screen_cls, "methods"):
            options["methods"] = screen_cls.methods

        async def view_func(*args, **kwargs):
            return await instance(*args, **kwargs)

        view_func.__name__ = instance.__name__
        self.quart.add_url_rule(path, view_func=view_func, **options)

    def add_screens(self, rules: dict[str, type]) -> None:
        for route, screen_cls in rules.items():
            self.add_screen(route, screen_cls)

    def add_router(self, path: str, view_func: Callable, **options) -> None:
        self.quart.add_url_rule(path, view_func=view_func, **options)

    def add_routers(self, rules: dict[str, Callable]) -> None:
        for route, func in rules.items():
            self.add_router(route, func)

    def before_request(self, func: Callable) -> None:
        self.quart.before_request(func)

    def after_request(self, func: Callable) -> None:
        self.quart.after_request(func)

    def set_error_page(self, code: int, screen_cls: type) -> None:
        instance = screen_cls()
        instance._app = self

        async def handler(error):
            return await instance(error)

        self.quart.register_error_handler(code, handler)

    def _register_default_error_handlers(self) -> None:
        @self.quart.errorhandler(404)
        async def _default_404(e):
            return await make_response(
                "<html><body style='font-family:sans-serif;text-align:center;padding:60px'>"
                "<h1>404</h1><p>Страница не найдена</p>"
                "<a href='/'>На главную</a></body></html>",
                404,
            )

        @self.quart.errorhandler(500)
        async def _default_500(e):
            return await make_response(
                "<html><body style='font-family:sans-serif;text-align:center;padding:60px'>"
                "<h1>500</h1><p>Внутренняя ошибка сервера</p></body></html>",
                500,
            )

    def on_start(self, func: Callable) -> None:
        self._startup_hooks.append(func)

    def on_stop(self, func: Callable) -> None:
        self._shutdown_hooks.append(func)

    async def _run_hooks(self, hooks: list[Callable]) -> None:
        for hook in hooks:
            try:
                result = hook()
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:
                print(f"[AsyncApp] Hook error in {hook.__name__}: {exc}")

    def load_config(self, path: str, encoding: str = "utf-8") -> None:
        if not os.path.exists(path):
            print(f"[AsyncApp] Config file not found: {path}")
            return
        try:
            self.config = JsonDict(path, encoding)
        except Exception as exc:
            print(f"[AsyncApp] Config load error: {exc}")

    @property
    def config(self) -> dict[str, Any]:
        return self.__config

    @config.setter
    def config(self, value):
        prefix = ""
        if isinstance(value, dict):
            if value.get("static_folder"):
                self.quart.static_folder = os.path.join(self.project_root, value["static_folder"])
            if value.get("template_folder"):
                self.quart.template_folder = os.path.join(self.project_root, value["template_folder"])

            if value.get("routers") and value.get("routers") != "auto":
                if value.get("screen_path"):
                    prefix = value["screen_path"].replace("/", ".") + "."
                for route, func_name in value["routers"].items():
                    try:
                        cls = getattr(import_module(prefix + func_name), func_name)
                        self.add_screen(route, cls)
                    except (ImportError, AttributeError) as exc:
                        print(f"[AsyncApp] Screen load error '{func_name}': {exc}")

            if value.get("routers") == "auto":
                self._auto_discover_screens(value.get("screen_path", "screens"))

            if value.get("root_path"):
                self.quart.root_path = value["root_path"]

            for prop, val in value.items():
                self.__config[prop] = val

        elif isinstance(value, JsonDict):
            self.config = value.dictionary

    def _auto_discover_screens(self, screen_path: str) -> None:
        screen_dir = os.path.join(self.project_root, screen_path)
        if not os.path.isdir(screen_dir):
            print(f"[AsyncApp] Screen directory not found: {screen_dir}")
            return

        prefix = screen_path.replace("/", ".").replace("\\", ".") + "."

        for filename in os.listdir(screen_dir):
            if filename.startswith("__") or not filename.endswith(".py"):
                continue

            mod_name = filename.replace(".py", "")
            try:
                module = import_module(prefix + mod_name)
            except ImportError as exc:
                print(f"[AsyncApp] Import error '{mod_name}': {exc}")
                continue

            for _, cls in inspect.getmembers(module, inspect.isclass):
                if not issubclass(cls, AsyncScreen) or cls is AsyncScreen:
                    continue
                if not hasattr(cls, "route"):
                    continue
                try:
                    routes = cls.route if isinstance(cls.route, list) else [cls.route]
                    for route in routes:
                        self.add_screen(route, cls)
                except Exception as exc:
                    print(f"[AsyncApp] Screen registration error '{cls.__name__}': {exc}")

    def enable_health_endpoint(self) -> None:
        if self._health_enabled:
            return

        async def health():
            return {"status": "ok", "app": self.app_name}

        self.quart.add_url_rule("/health", "aengine_health", health, methods=["GET"])
        self._health_enabled = True

    def enable_metrics_endpoint(self) -> None:
        if self._metrics_enabled:
            return

        async def metrics():
            body = (
                "# HELP requests_total Total HTTP requests handled by AsyncApp\n"
                "# TYPE requests_total counter\n"
                f"requests_total {self._request_count}\n"
            )
            return Response(body, mimetype="text/plain")

        self.quart.add_url_rule("/metrics", "aengine_metrics", metrics, methods=["GET"])
        self._metrics_enabled = True

    async def run(self) -> None:
        host: Optional[str] = self.config.get("host")
        port: Optional[int] = self.config.get("port")
        if not host:
            print("[AsyncApp] Missing host in config.")
            return
        if not port:
            print("[AsyncApp] Missing port in config.")
            return

        self._register_default_error_handlers()
        await self._run_hooks(self._startup_hooks)

        if host == "0.0.0.0":
            try:
                addrs = {
                    info[4][0]
                    for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
                }
                for addr in addrs:
                    print(f"Running '{self.app_name}' on http://{addr}:{port}")
            except socket.gaierror:
                print(f"Running '{self.app_name}' on http://0.0.0.0:{port}")
        else:
            print(f"Running '{self.app_name}' on http://{host}:{port}")

        try:
            await self.quart.run_task(host=host, port=port, debug=self.config.get("debug") or False)
        finally:
            await self._run_hooks(self._shutdown_hooks)
