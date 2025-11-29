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

# --- Helper Functions ---

def _get_site_packages_path():
    """
    Attempts to robustly determine the site-packages directory
    of the currently active Python environment (virtual environment).
    """
    # 1. Check if we are in a virtual environment
    is_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not is_venv:
        return None 
    
    venv_root = Path(sys.prefix)
    
    # 2. Typical Linux/macOS path: venv/lib/pythonX.Y/site-packages
    lib_dir = venv_root / "lib"
    python_version_dir = f"python{sys.version_info.major}.{sys.version_info.minor}"
    site_packages = lib_dir / python_version_dir / "site-packages"
    
    if site_packages.is_dir():
        return str(site_packages)

    # 3. Fallback for Windows/others: venv/Lib/site-packages
    site_packages_win = venv_root / "Lib" / "site-packages"
    if site_packages_win.is_dir():
        return str(site_packages_win)
        
    return None 


# --- Build Steps ---

def run_command(cmd, cwd=None, check=True, env=None):
    """Run command, print it, capture output, raise on error. Accepts optional env dict."""
    print(f"\nRunning: {' '.join(cmd)}")
    # Pass the optional env dictionary to subprocess.run
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check, env=env)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        # Only print stderr if it's not a success and check is False, or if it contains error text
        if check or "error" in result.stderr.lower():
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
    Attempts to use uv, then Poetry, then falls back to `python -m build`.
    """
    print("1. Building clean Python Wheel (no .pyc)…")
    
    # Check for uv
    use_uv = shutil.which("uv") is not None and Path("pyproject.toml").exists()
    # Check for Poetry (keep existing logic)
    use_poetry = not use_uv and shutil.which("poetry") is not None and (Path("pyproject.toml").exists() or Path("setup.py").exists())
    
    if use_uv:
        print("   Using uv to build wheel...")
        try:
            # uv build automatically handles pyproject.toml and outputs to dist/
            run_command(["uv", "build"])
        except subprocess.CalledProcessError:
            print("ERROR: Failed to build wheel with uv. Ensure uv is installed and pyproject.toml is correct.")
            sys.exit(1)
            
    elif use_poetry:
        print("   Using Poetry to build wheel...")
        try:
            # Poetry automatically handles dependencies and pyproject.toml
            run_command(["poetry", "build", "-f", "wheel", "--output", str(dist_dir)])
        except subprocess.CalledProcessError:
            print("ERROR: Failed to build wheel with Poetry. Ensure Poetry is configured correctly.")
            sys.exit(1)
            
    else:
        print("   Using python -m build (uv/Poetry not found/configured)...")
        # Assuming 'build' is installed (pip install build)
        try:
            # Use the virtual environment's Python to run the build module
            run_command([PYTHON_BIN, "-m", "build", "--wheel", "--outdir", str(dist_dir)])
        except subprocess.CalledProcessError:
            print("ERROR: Failed to build wheel with 'python -m build'. Ensure the 'build' package is installed in your virtual environment and pyproject.toml is correct.")
            sys.exit(1)

    # All build tools output the wheel to the 'dist' directory
    wheels = list(dist_dir.glob("*.whl"))
    if not wheels:
        raise FileNotFoundError("No wheel built by the chosen build tool. Check your dist directory.")
    
    # Find the latest built wheel (essential when using uv which might build multiple formats)
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
    
    # Explicit check for the shiv executable
    if not shutil.which("shiv"):
        print("\n" + "="*70)
        print("CRITICAL ERROR: 'shiv' executable not found in your PATH.")
        print("Please ensure you have installed shiv (e.g., `pip install shiv`).")
        print("If installed, ensure your virtual environment is active.")
        print("="*70)
        sys.exit(1)
    
    # Use PYTHONDONTWRITEBYTECODE to ensure no .pyc files are written during shiv creation
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    
    site_packages_path = _get_site_packages_path()
    site_packages_arg = ["--site-packages", site_packages_path] if site_packages_path else []

    if site_packages_path:
        print(f"   Using --site-packages from VENV: {site_packages_path}")
    
    # The --pre-zip-dir flag maps the local frontend/dist folder 
    # to the 'static' directory inside the zip file.
    cmd = [
        "shiv",
        str(wheel_path),
        "--no-deps", # <-- New: Tell shiv to ignore wheel dependencies and rely on site-packages
        "-e", entry_point,
        "-o", str(out_path),
        "-p", "/usr/bin/env python3", # Standard Linux/macOS shebang
        "--compressed",
        "--pre-zip-dir", f"{FRONTEND_DIST_DIR}:static", # Map frontend/dist to static/
        "--no-cache", # Do not bake .pyc—cache at runtime (faster build, smaller file)
        "--build-id", "production",
        *site_packages_arg # Include the site-packages argument if found
    ]
    
    try:
        run_command(cmd, env=env)
        out_path.chmod(0o755)
        print(f"SUCCESS: Shiv built at {out_path.resolve()}")
        print("To run, execute:")
        print(f"   ./{out_path.name}")
    except subprocess.CalledProcessError:
        print("ERROR: Failed to build shiv executable. This usually indicates an issue with 'shiv' itself or dependency resolution inside the archive.")
        print("Since you are using '--site-packages', this might be due to native code dependencies (like msgspec) being included incorrectly. The '--no-deps' flag has been added as a common fix for this scenario.")
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
