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
