"""
SQLite + SQLModel persistence layer.

The DB file lives at ``backend/app.db`` (see ``app.core.paths``). It survives
across server restarts, so jobs and applications (with their Gemini screening
results) are no longer lost on reload.

To wipe local state for development, delete the file or run:
    rm backend/app.db
"""

from sqlmodel import Session, SQLModel, create_engine

from app.core.paths import DB_PATH

# Import models so SQLModel.metadata is populated before create_all().
from app.models import Application, Job  # noqa: F401

DATABASE_URL = f"sqlite:///{DB_PATH}"

# ``check_same_thread=False`` is required because FastAPI may dispatch
# requests across threads while reusing the engine.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


def init_db() -> None:
    """Create all tables if they don't already exist."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a transactional session per request."""
    with Session(engine) as session:
        yield session
