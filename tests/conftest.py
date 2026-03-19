# pytest configuration and fixtures
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from AEngineApps.async_app import AsyncApp
from AEngineApps.async_screen import AsyncScreen


@pytest.fixture
def app():
    """Create test application instance."""
    test_app = AsyncApp("TestApp", debug=True)
    test_app.config = {
        "host": "127.0.0.1",
        "port": 5000,
        "secret_key": "test-secret-key-for-testing-only",
        "debug": True
    }
    return test_app


@pytest.fixture
async def client(app):
    """Create test client."""
    return app.quart.test_client()


@pytest.fixture
def sample_screen():
    """Sample screen for testing."""
    class TestScreen(AsyncScreen):
        route = "/test"
        
        async def run(self):
            return self.json({"status": "ok"})
    
    return TestScreen
