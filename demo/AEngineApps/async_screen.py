"""
AsyncScreen -- asynchronous base screen for AsyncApp.
"""

from __future__ import annotations

import os
from typing import Any

from quart import (
    abort,
    flash as quart_flash,
    jsonify,
    redirect as quart_redirect,
    render_template,
    request,
    session,
)


class AsyncScreen:
    """Base async screen class with the same helpers as Screen."""

    route: str = "/"
    methods: list[str] = ["GET"]
    _app = None

    def __init__(self) -> None:
        self.__name__ = self.__class__.__name__

    async def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError(f"Method 'run' for screen '{self.__name__}' is not implemented")

    async def __call__(self, *args, **kwargs) -> Any:
        return await self.run(*args, **kwargs)

    async def render(self, template: str, **context) -> str:
        return await render_template(template, **context)

    def redirect(self, url: str, code: int = 302):
        return quart_redirect(url, code)

    def json(self, data: Any, status: int = 200):
        response = jsonify(data)
        response.status_code = status
        return response

    @property
    def request(self):
        return request

    @property
    def app(self):
        return self._app

    @property
    def session(self):
        return session

    def abort(self, code: int, *args, **kwargs):
        abort(code, *args, **kwargs)

    async def flash(self, message: str, category: str = "message"):
        await quart_flash(message, category)

    @property
    def client_ip(self) -> str:
        forwarded = self.request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.request.remote_addr or "127.0.0.1"

    async def save_file(self, field_name: str, save_path: str) -> bool:
        files = await self.request.files
        file = files.get(field_name)
        if file and file.filename != "":
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            result = file.save(save_path)
            if hasattr(result, "__await__"):
                await result
            return True
        return False
