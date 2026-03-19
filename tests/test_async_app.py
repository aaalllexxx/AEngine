# Tests for AsyncApp
import pytest
from AEngineApps.async_app import AsyncApp
from AEngineApps.async_screen import AsyncScreen


@pytest.mark.asyncio
async def test_app_creation():
    """Test basic app creation."""
    app = AsyncApp("TestApp")
    assert app.app_name == "TestApp"
    assert app.quart is not None


@pytest.mark.asyncio
async def test_health_endpoint(app, client):
    """Test health check endpoint."""
    app.enable_health_endpoint()
    
    response = await client.get("/health")
    assert response.status_code == 200
    
    data = await response.get_json()
    assert "status" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(app, client):
    """Test metrics endpoint."""
    app.enable_metrics_endpoint()
    
    response = await client.get("/metrics")
    assert response.status_code == 200
    
    text = await response.get_data(as_text=True)
    assert "requests_total" in text


@pytest.mark.asyncio
async def test_screen_routing(app, client, sample_screen):
    """Test screen routing."""
    app.add_screen("/test", sample_screen)
    
    response = await client.get("/test")
    assert response.status_code == 200
    
    data = await response.get_json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_config_validation(app):
    """Test config validation."""
    app.config = {
        "host": "0.0.0.0",
        "port": 8000,
        "secret_key": "test-key"
    }
    
    assert app.config["host"] == "0.0.0.0"
    assert app.config["port"] == 8000
