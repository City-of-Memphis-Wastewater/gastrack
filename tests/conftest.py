# --- tests/conftest.py ---
import pytest
import httpx
from starlette.testclient import TestClient

# Ensure the database is initialized before any tests run
from src.gastrack.db.connection import DB_PATH
from src.gastrack.core.server import get_app
import src.gastrack.db.crud # Needed to trigger init_db


@pytest.fixture(scope="session")
def app():
    """Fixture to get the Starlette app instance."""
    # We use a non-default port here to avoid conflicts if the main server is running
    return get_app()

@pytest.fixture(scope='session')
def client(app):
    """
    Synchronous fixture providing the Starlette TestClient.
    The TestClient wraps the app and exposes the HTTPX client object.
    """
    with TestClient(app, base_url="http://test") as test_client:
        # We yield the actual HTTPX client object managed by TestClient
        # This allows us to use it in async tests
        yield test_client
