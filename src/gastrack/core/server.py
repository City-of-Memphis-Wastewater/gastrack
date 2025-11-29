# src/gastrack/core/server.py
import uvicorn
import os
from pathlib import Path 
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse


# Import the API routes
from src.gastrack.api.handlers import api_routes
from src.gastrack.db.connection import init_db
from src.gastrack.core.environment import is_production_build

# Define the directory where the built frontend files reside using Path
SERVER_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SERVER_DIR.parent.parent.parent
STATIC_DIR = PROJECT_ROOT / "frontend" / "dist"

# Placeholder for your API handlers
async def homepage(request):
    return JSONResponse({"status": "ok", "message": "GasTrack API is running"})

def get_app(): # <-- no arguments needed
    """Creates and returns the Starlette application instance."""

    debug = not is_producton_build()
    
    # Explicitly initialize the database upon app creation
    init_db(conn=None) # it's this one, which was acutally hard won

    # Define middleware, especially for development CORS if needed
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=['*'],  # Restrict this in production
            allow_methods=['*'],
            allow_headers=['*']
        )
    ]

    # Define Core Routes
    routes = []

    # Append the new API routes under a /api prefix
    from src.gastrack.api.handlers import api_routes # Deferred import for circular dependency
    api_mount = Mount("/api", routes=api_routes)
    routes.append(api_mount)

    # NOTE: Moving this after the API mount ensures API routes get precedence.
    routes.append(
        Mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    )

    app = Starlette(
        routes=routes,
        middleware=middleware,
        debug=debug # Set to False for production PYZ file
    )
    return app # <-- Returns the app instance

# Note: Application lifecycle events (on_startup/on_shutdown) 
# for database management are often defined here.

# For now, we rely on the logic in src.gastrack.db.connection 
# to lazily initialize the database file on first import.

def run_server(port: int):
    app_instance = get_app()
    uvicorn.run(app_instance, host="127.0.0.1", port=port)
