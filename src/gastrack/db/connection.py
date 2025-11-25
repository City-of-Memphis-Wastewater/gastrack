import duckdb
import os

# Define the path to the DuckDB database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gastrack.duckdb")

# Define the path to the SQL schema file
SQL_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init_schema.sql")


def get_db_connection():
    """Establishes and returns a DuckDB connection."""
    # Use 'read_only=False' to allow writing
    return duckdb.connect(database=DB_PATH, read_only=False)

def init_db(conn: duckdb.DuckDBPyConnection):
    """Initializes the database schema if tables do not exist."""
    print("Initializing DuckDB schema...")
    try:
        with open(SQL_SCHEMA_PATH, 'r') as f:
            sql_script = f.read()
        
        # Execute the entire SQL script
        conn.execute(sql_script)
        print("DuckDB schema initialized successfully.")
    except Exception as e:
        print(f"Error initializing database schema: {e}")

# This block ensures the database file and schema are created
# the first time any component imports 'connection.py'
if not os.path.exists(DB_PATH):
    print(f"Database file not found at {DB_PATH}. Creating and initializing...")
    conn = get_db_connection()
    init_db(conn)
    conn.close()
    
