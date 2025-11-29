# src/gastrack/core/environment.py
from __future__ import annotations

"""
Carry introspection and build checks.
Consider migrating functions to pyhabitat package.
"""

import sys
from typing import Any

def is_production_build() -> bool:
    """
    Returns True when running from a built/frozen executable (shiv .pyz or PyInstaller).
    False when running from source (development, tests, etc.).
    """
    # 1. Explicit shiv build ID — most explicit
    if getattr(sys, "shiv_build_id", None) == "production":
        return True

    # 2. PyInstaller (Windows .exe, Linux ELF, macOS .app) — official detection
    if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
        return True

    # 3. Fallback: running directly from a .pyz file (works even without --build-id)
    if sys.argv and sys.argv[0] and (sys.argv[0].endswith(('.pyz', '.exe'))):
        return True

    return False
