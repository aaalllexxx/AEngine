"""
AEngineApps — OOP framework for building webview/web apps.
"""

from AEngineApps.app import App
from AEngineApps.screen import Screen
from AEngineApps.api import API
from AEngineApps.service import Service
from AEngineApps.global_storage import GlobalStorage
from AEngineApps.json_dict import JsonDict

__all__ = [
    "App",
    "Screen",
    "API",
    "Service",
    "GlobalStorage",
    "JsonDict",
]

# ─── Async-слой (Quart) — опционален: грузится, только если установлен quart ───
try:
    from AEngineApps.async_app import AsyncApp
    from AEngineApps.async_screen import AsyncScreen
    from AEngineApps.async_api import AsyncAPI

    __all__ += ["AsyncApp", "AsyncScreen", "AsyncAPI"]
except ImportError:
    # Quart не установлен — синхронная часть работает без него.
    pass
