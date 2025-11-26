# src/gastrack/core/server.py
import os
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from src.gastrack.api.handlers import api_routes

# Determine the base path for static files.
# When run from a PYZ file, __file__ points to the file *inside* the archive.
# The static files (built Svelte app) should be alongside the module's directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# The frontend assets are expected to be in a 'static' directory within the zip/package
STATIC_DIR = os.path.join(BASE_DIR, 'static') 
# In a typical dev setup, the base path is up two levels from core/server.py
# We can add checks here to detect PYZ mode if needed, but relative path is often enough.

async def homepage(request):
    """Serves the index.html from the Svelte build."""
    index_path = os.path.join(STATIC_DIR, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            content = f.read()
        return HTMLResponse(content)
    # Fallback for when the build hasn't happened or paths are wrong
    return HTMLResponse("<h1>GasTrack Backend Running</h1><p>Frontend assets not found. Run 'cd frontend && npm run build' and rebuild the PYZ file.</p>")


def get_app():
    """Initializes and returns the Starlette application."""
    # Define middleware, especially for development CORS if needed
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=['*'],  # Restrict this in production
            allow_methods=['*'],
            allow_headers=['*']
        )
    ]

    routes = [
        # Route for the single page application (serves index.html)
        Route("/", homepage),
        # API routes from handlers.py
        *api_routes
    ]

    app = Starlette(
        routes=routes,
        middleware=middleware,
        debug=True # Set to False for production PYZ file
    )

    # Mount the StaticFiles handler to serve Svelte assets (JS, CSS, etc.)
    # The 'static' directory must exist in the PYZ file or on disk.
    app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')
    
    return app

if __name__ == '__main__':
    # This is often used only for local development/testing
    import uvicorn
    # In development, the static directory is usually frontend/dist
    dev_static_dir = os.path.join(os.path.dirname(BASE_DIR), 'frontend', 'dist')
    
    # Simple check to use the correct static path for development
    if os.path.exists(dev_static_dir) and not os.environ.get('GASTRACK_PYZ_MODE'):
        print(f"Running in Development Mode, serving from: {dev_static_dir}")
        STATIC_DIR = dev_static_dir
        app = get_app()
    else:
        app = get_app()
        
    uvicorn.run(app, host="0.0.0.0", port=8000)