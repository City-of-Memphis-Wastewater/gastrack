#!/bin/bash
# build-scripts/setup_python.sh

# 1. Install Dependencies using uv
echo "Installing Python dependencies with uv..."
uv venv
source .venv/bin/activate

uv pip install starlette uvicorn msgspec duckdb python-multipart typer

# 2. Create Python Entry Point (main.py)
echo "Creating src/main.py..."
cat << 'EOF' > src/main.py
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
EOF

# 3. Create API Server File (src/gastrack/core/server.py)
echo "Creating src/gastrack/core/server.py..."
cat << 'EOF' > src/gastrack/core/server.py
# src/gastrack/core/server.py
import uvicorn
import os
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse

# Placeholder for your API handlers
async def homepage(request):
    return JSONResponse({"status": "ok", "message": "GasTrack API is running"})

# Placeholder for static file serving (Svelte SPA)
# The 'frontend' directory will contain your compiled Svelte build
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'frontend', 'dist')

routes = [
    Route("/", homepage),
    # Add API routes here: /api/data, /api/calc, etc.
    # Serve static assets (Svelte build)
    Mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
]

app = Starlette(
    debug=True,
    routes=routes
)

def run_server(port: int):
    uvicorn.run(app, host="127.0.0.1", port=port)
EOF

echo "Python setup complete. Run 'source .venv/bin/activate' and then 'python src/main.py start'."
