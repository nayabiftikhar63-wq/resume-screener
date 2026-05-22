"""Centralised filesystem paths.

Resolved from the location of this file so they stay correct regardless of
where the process is started from. ``BACKEND_DIR`` is the ``backend/`` folder
and ``PROJECT_ROOT`` is the repository root.
"""

from pathlib import Path

# this file lives at  <repo>/backend/app/core/paths.py
BACKEND_DIR: Path = Path(__file__).resolve().parents[2]
PROJECT_ROOT: Path = BACKEND_DIR.parent

UPLOAD_DIR: Path = BACKEND_DIR / "uploads"
DB_PATH: Path = BACKEND_DIR / "app.db"
ENV_FILE: Path = BACKEND_DIR / ".env"

FRONTEND_DIST: Path = PROJECT_ROOT / "frontend" / "dist"
