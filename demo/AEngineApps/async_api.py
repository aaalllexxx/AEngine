"""
AEngineApps.async_api — асинхронный аналог API для AsyncApp (на базе Quart).
"""

from __future__ import annotations

import inspect
from typing import Any

from AEngineApps.async_screen import AsyncScreen


class AsyncAPI(AsyncScreen):
    """
    Базовый класс для асинхронных REST API.
    Маршрутизирует HTTP-запросы в async-методы (get, post, put, delete, patch).
    Автоматически конвертирует dict/list в JSON-ответы.

    Пример:
        class UserAPI(AsyncAPI):
            route = "/api/user"
            methods = ["GET", "POST"]

            async def get(self):
                return {"name": "Alex"}

            async def post(self):
                data = await self.request.get_json()
                return {"status": "created"}, 201
    """

    async def run(self, *args, **kwargs) -> Any:
        method = self.request.method.lower()

        if not hasattr(self, method):
            return self.json({"error": "Method Not Allowed"}, 405)

        handler = getattr(self, method)
        result = handler(*args, **kwargs)
        if inspect.isawaitable(result):
            result = await result

        if isinstance(result, tuple):
            data, status = result
            if isinstance(data, (dict, list)):
                return self.json(data, status)
            return result
        if isinstance(result, (dict, list)):
            return self.json(result)
        return result

    # ─── API Хелперы ──────────────────────────────────────────

    async def require_keys(self, required_keys: list[str]) -> tuple[bool, str]:
        """Проверка наличия обязательных ключей в JSON-теле запроса."""
        data = await self.request.get_json(silent=True)
        if not isinstance(data, dict):
            return False, "JSON body"
        for key in required_keys:
            if key not in data:
                return False, key
        return True, ""

    def get_arg(self, key: str, type_func=str, default=None):
        """Безопасное получение и типизация query-параметра (?key=value)."""
        val = self.request.args.get(key)
        if val is None:
            return default
        try:
            return type_func(val)
        except (ValueError, TypeError):
            return default
