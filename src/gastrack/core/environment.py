# src/gastrack/core/environment.py
from __future__ import annotations

"""
Carry introspection and build checks.
Consider migrating functions to pyhabitat package.
"""

def is_production_build() -> bool:
    """Shiv sets sys.shiv_build_id when --build-id is used"""
    return getattr(sys, "shiv_build_id", None) == "production"

def is_production() -> bool:
    """Shiv sets sys.shiv_build_id when --build-id is used (in build_shiv.pyz)"""
   
    return (
        getattr(sys, "shiv_build_id", None) == "production"
        or (hasattr(sys, "frozen") and getattr(sys, "_MEIPASS", None))  # PyInstaller fallback
        or str(sys.argv[0]).endswith(('.pyz', '.exe'))
    )
