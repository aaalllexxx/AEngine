"""
test_demo_deps.py — Регрессионные тесты зависимостей security-demo.

Фиксируют баг 3.2.0: из ``security-demo/requirements.txt`` была ошибочно удалена
зависимость ``pywebview``. Поскольку ``AEngineApps`` импортирует ``webview`` на
уровне модуля, без неё стенд не импортируется даже в web-режиме.
"""

import os
import re
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEMO_REQUIREMENTS = os.path.join(REPO_ROOT, "security-demo", "requirements.txt")


def _declared_distributions() -> set[str]:
    """Имена дистрибутивов, объявленных в requirements.txt (в нижнем регистре)."""
    names: set[str] = set()
    with open(DEMO_REQUIREMENTS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # отрезаем спецификаторы версий/маркеры: flask>=2.3.0 → flask
            name = re.split(r"[<>=!~;\[\s]", line, maxsplit=1)[0]
            if name:
                names.add(name.lower())
    return names


@pytest.mark.parametrize("distribution", ["flask", "psutil", "pywebview"])
def test_demo_requirements_declares(distribution):
    """Все рантайм-зависимости стенда объявлены в requirements.txt."""
    assert distribution in _declared_distributions(), (
        f"'{distribution}' отсутствует в {DEMO_REQUIREMENTS}. "
        f"Стенд не запустится без неё."
    )


def test_aengineapps_requires_webview():
    """AEngineApps импортирует webview на уровне модуля → pywebview обязателен.

    Если этот импорт когда-нибудь станет ленивым, тест подсветит, что связь
    'pywebview обязателен для импорта AEngineApps' изменилась и документацию/
    requirements нужно пересмотреть.
    """
    import AEngineApps  # noqa: F401  (импорт ради побочного эффекта)

    assert "webview" in sys.modules, (
        "AEngineApps больше не импортирует webview на уровне модуля — "
        "пересмотрите необходимость pywebview в requirements и документации."
    )
