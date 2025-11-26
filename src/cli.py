# --- src/gastrack/cli.py ---

import typer
from rich.console import Console

# We'll use the main function from src.gastrack.core.server
from src.gastrack.core.server import run_server
from src.gastrack.db.connection import DB_PATH, init_db

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
    """Re-run schema + default factors (safe to run multiple times)."""
    init_db()
    console.print("[bold cyan]Database schema and default factors ensured.[/bold cyan]")

@app.command()
def db_clear():
    """Delete the database file."""
    if DB_PATH.exists():
        DB_PATH.unlink()
        console.print(f"[bold yellow]Database deleted:[/bold yellow] {DB_PATH}")
    else:
        console.print("[bold yellow]No database file to delete.[/bold yellow]")

@app.command()
def db_path():
    """Show where the database lives."""
    console.print(f"Database path: {DB_PATH.resolve()}")

if __name__ == "__main__":
    app()


