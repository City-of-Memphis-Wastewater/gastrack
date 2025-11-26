# --- src/gastrack/db/connection.py ---
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Define the paths relative to the current file
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "gastrack.db"
SQL_SCHEMA_PATH = BASE_DIR / "src" / "gastrack" / "db" / "init_schema.sql"

'''
@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # gives dict-like rows (perfect for msgspec)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")   # safe concurrent writes
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
'''

@contextmanager
def get_db_connection():
    """Public function – used everywhere in your code."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(conn=None):
    """Public function – called from cli.py, server.py, tests, etc."""
    close_when_done = conn is None
    if conn is None:
        with get_db_connection() as conn:
            _run_schema(conn)
            return  # early return – connection auto-closes

    _run_schema(conn)
    if close_when_done:
        conn.close()

def _run_schema(conn):
    print("Initializing SQLite schema...")
    schema_sql = SQL_SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)
    print("SQLite schema initialized successfully.")


# Auto-create DB + init on first import
if not DB_PATH.exists():
    print(f"Database not found at {DB_PATH}. Creating and initializing...")
    init_db()

'''
# Auto-create DB + run schema on first import (exactly like your old DuckDB code)
if not DB_PATH.exists():
    print(f"Database not found at {DB_PATH}. Creating and initializing...")
    with get_db_connection() as conn:
        schema_sql = SQL_SCHEMA_PATH.read_text()
        conn.executescript(schema_sql)
        print("SQLite database initialized successfully.")

'''