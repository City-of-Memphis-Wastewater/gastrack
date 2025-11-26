import os
import shutil
import subprocess
import sys
from pathlib import Path
import glob

# --- Configuration ---
PROJECT_NAME = "gastrack"
SHIV_FILENAME = f"{PROJECT_NAME}.pyz"
DIST_DIR = Path("dist") # Where the final executable goes
FRONTEND_DIST_DIR = Path("frontend") / "dist"
PYTHON_BIN = sys.executable

# The entry point must point to a callable that returns the Starlette application instance
# Format: package.module:function
ENTRY_POINT = f"{PROJECT_NAME}.core.server:get_app" 

# --- Build Steps ---

def run_command(cmd, cwd=None, check=True):
    """Run command, print it, capture output, raise on error."""
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result

def clean_dist(dist_dir: Path):
    """Nuke old build artifacts."""
    dist_dir.mkdir(exist_ok=True)
    print(f"Cleaning {dist_dir}...")
    for item in dist_dir.glob(f"{PROJECT_NAME}*"):
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

def build_wheel(dist_dir: Path) -> Path:
    """
    Builds the Python Wheel for the gastrack package.
    Assumes `pyproject.toml` or `setup.py` exists to define the package.
    We rely on `build` to create the wheel in the `dist_dir`.
    """
    print("1. Building clean Python Wheel (no .pyc)…")
    # Using the standard build module which respects PYTHONDONTWRITEBYTECODE=1
    # We must ensure we are in the project root for this command to work.
    
    # Assuming 'build' is installed (pip install build)
    try:
        run_command([PYTHON_BIN, "-m", "build", "--wheel", "--outdir", str(dist_dir)])
    except subprocess.CalledProcessError:
        print("ERROR: Failed to build wheel. Ensure the 'build' package is installed and pyproject.toml is correct.")
        sys.exit(1)

    wheels = list(dist_dir.glob("*.whl"))
    if not wheels:
        raise FileNotFoundError("No wheel built by python -m build.")
    
    # Find the latest built wheel
    latest_wheel = max(wheels, key=lambda f: f.stat().st_mtime)
    print(f"   Built wheel: {latest_wheel.name}")
    return latest_wheel

def build_frontend():
    """Builds the Svelte frontend into the dist folder."""
    print("2. Building Svelte frontend (npm run build)...")
    if not (Path("frontend") / "package.json").exists():
        print("   Skipping frontend build: 'frontend/package.json' not found.")
        return True

    # Check if the dist folder exists and is non-empty
    if not FRONTEND_DIST_DIR.exists() or not list(FRONTEND_DIST_DIR.glob('*')):
        # Run npm commands
        try:
            # Assumes 'npm run build' is defined in frontend/package.json
            run_command(["npm", "run", "build"], cwd="frontend")
            if not FRONTEND_DIST_DIR.exists() or not list(FRONTEND_DIST_DIR.glob('*')):
                 print(f"ERROR: Frontend build succeeded but did not create {FRONTEND_DIST_DIR}.")
                 sys.exit(1)
        except subprocess.CalledProcessError:
            print("ERROR: Failed to run 'npm run build'. Ensure npm is installed and the command works.")
            sys.exit(1)
    else:
         print("   Frontend build already exists and is non-empty. Skipping build.")


def build_shiv(wheel_path: Path, entry_point: str, out_path: Path):
    """
    Build shiv .pyz from WHEEL and include static assets.
    --pre-zip-dir is used to inject the static assets into the archive root
    under the 'static' directory, which the server expects.
    """
    print(f"3. Building Shiv executable → {out_path.name}")
    
    # Use PYTHONDONTWRITEBYTECODE to ensure no .pyc files are written during shiv creation
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    
    # The --pre-zip-dir flag maps the local frontend/dist folder 
    # to the 'static' directory inside the zip file.
    cmd = [
        "shiv",
        str(wheel_path),
        "-e", entry_point,
        "-o", str(out_path),
        "-p", "/usr/bin/env python3", # Standard Linux/macOS shebang
        "--compressed",
        "--pre-zip-dir", f"{FRONTEND_DIST_DIR}:static", # Map frontend/dist to static/
        "--no-cache" # Do not bake .pyc—cache at runtime (faster build, smaller file)
    ]
    
    try:
        run_command(cmd, env=env)
        out_path.chmod(0o755)
        print(f"SUCCESS: Shiv built at {out_path.resolve()}")
        print("To run, execute:")
        print(f"   ./{out_path.name}")
    except subprocess.CalledProcessError:
        print("ERROR: Failed to build shiv executable. Ensure 'shiv' is installed (pip install shiv).")
        sys.exit(1)


def main():
    # Enforce no .pyc files during the whole process
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1" 

    clean_dist(DIST_DIR)
    
    # 1. Build the frontend assets first
    build_frontend() 

    # 2. Build the Python package wheel
    wheel_path = build_wheel(DIST_DIR)
    
    # 3. Build the final Shiv executable
    shiv_path = DIST_DIR / SHIV_FILENAME
    build_shiv(wheel_path, ENTRY_POINT, shiv_path)
    
    print("\n" + "="*70)
    print("SHIV BUILD COMPLETE")
    print(f"The final executable is: {shiv_path}")
    print("="*70)

if __name__ == "__main__":
    main()