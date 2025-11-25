# src/main.py
# Main entry point for CLI and Server
import typer
from src.gastrack.core.server import run_server

app = typer.Typer(help="GasTrack: Biogas Data Tracker CLI and Server Runner.")

@app.command()
def start(port: int = 8000):
    """
    Start the Uvicorn ASGI server.
    """
    typer.echo(f"Starting GasTrack server on http://localhost:{port}")
    run_server(port)

@app.command()
def report(month: str = typer.Argument(..., help="Month in YYYY-MM format (e.g., 2025-09)")):
    """
    Generate a monthly biogas report.
    """
    typer.echo(f"Generating monthly report for: {month}")
    # Calculation logic will go here

if __name__ == "__main__":
    app()
