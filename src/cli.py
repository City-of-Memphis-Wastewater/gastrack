# --- src/gastrack/cli.py ---

import typer
from rich.console import Console

# We'll use the main function from src.gastrack.core.server
from src.gastrack.core.server import run_server

app = typer.Typer(help="GasTrack Command Line Interface for managing the server, database, and utilities.")
console = Console()

@app.command()
def start(
    port: int = typer.Option(
        8000, 
        "--port", 
        "-p", 
        help="Port to run the Starlette server on."
    )
):
    """
    Starts the GasTrack API server using Uvicorn.
    """
    console.print(f"[bold green]Starting GasTrack API server on http://127.0.0.1:{port}[/bold green]")
    try:
        run_server(port)
    except Exception as e:
        console.print(f"[bold red]Server failed to start:[/bold red] {e}")

@app.command()
def db_init():
    """
    Forces initialization of the DuckDB schema and inserts base factors.
    """
    from src.gastrack.db.connection import get_db_connection, init_db
    
    with get_db_connection() as conn:
        init_db(conn)
    console.print("[bold cyan]DuckDB initialized and base factors inserted.[/bold cyan]")

@app.command()
def db_clear():
    """
    Wipes the DuckDB database file.
    """
    from src.gastrack.db.connection import DB_PATH
    if DB_PATH.exists():
        DB_PATH.unlink()
        console.print(f"[bold yellow]Database file wiped:[/bold yellow] {DB_PATH}")
    else:
        console.print("[bold yellow]No database file found to wipe.[/bold yellow]")


if __name__ == "__main__":
    app()