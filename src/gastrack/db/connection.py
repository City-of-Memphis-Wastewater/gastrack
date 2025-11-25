import duckdb
from pathlib import Path

# Define the paths relative to the current file
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "gastrack.duckdb"
SQL_SCHEMA_PATH = BASE_DIR / "init_schema.sql"

def get_db_connection():
    """Establishes and returns a DuckDB connection."""
    # Use 'read_only=False' to allow writing
    return duckdb.connect(database=DB_PATH, read_only=False)

def init_db(conn: duckdb.DuckDBPyConnection):
    """Initializes the database schema if tables do not exist."""
    print("Initializing DuckDB schema...")
    try:
        sql_script = SQL_SCHEMA_PATH.read_text()
        
        # Execute the entire SQL script
        conn.execute(sql_script)
        print("DuckDB schema initialized successfully.")
    except Exception as e:
        print(f"Error initializing database schema: {e}")

# This block ensures the database file and schema are created
# the first time any component imports 'connection.py'
if not DB_PATH.exists(): # Use Path.exists()
    print(f"Database file not found at {DB_PATH}. Creating and initializing...")
    conn = get_db_connection()
    init_db(conn)
    conn.close()
    
