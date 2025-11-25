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
    # FIX: Remove the 'await' keyword. client.get() is now synchronous.
    response = client.get("/api/factors") 
    
    assert response.status_code == 200
    data = response.json()
    
    # We still rely on the database cleanup happening in conftest.py
    assert isinstance(data, list)
    assert len(data) >= 4 # Check for the four factors inserted in init_schema.sql
    assert any(item["key"] == "EMF_NOX_LBS_MMBTU" for item in data)