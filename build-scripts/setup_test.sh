#!/usr/bin/env zsh

echo "Setting up testing environment (tests/ and dependencies)..."

# Create the tests directory
mkdir -p tests

# Install testing dependencies
uv add pytest httpx

# Create a basic conftest.py for common fixtures
cat << EOF > tests/conftest.py
import pytest
import httpx

from src.gastrack.core.server import run_server

@pytest.fixture(scope="session")
def app():
    """Fixture to get the Starlette app instance."""
    # We use a non-default port here to avoid conflicts if the main server is running
    return run_server()

@pytest.fixture
async def client(app):
    """Fixture for an asynchronous HTTPX test client."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
EOF

# Create a placeholder test file
cat << EOF > tests/test_api_factors.py
import pytest
from src.gastrack.db.connection import DB_PATH

# Ensure the database is clean before running tests that touch the DB
@pytest.fixture(scope="module", autouse=True)
def setup_db_for_test():
    """Wipes and re-initializes the database for a clean test run."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    # The first import of crud or connection will trigger re-initialization
    import src.gastrack.db.crud
    
    # We yield control back to the test runner
    yield
    
    # Cleanup: wipe the test DB after the module runs
    if DB_PATH.exists():
        DB_PATH.unlink()

@pytest.mark.asyncio
async def test_get_factors_success(client):
    """Test retrieving factors from the /api/factors endpoint."""
    response = await client.get("/api/factors")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 4 # Check for the four factors inserted in init_schema.sql
    assert any(item["key"] == "EMF_NOX_LBS_MMBTU" for item in data)
EOF

echo "Testing environment created. Run 'pytest' from the project root to execute."
