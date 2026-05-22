"""Shared test fixtures.

Uses a fresh in-memory SQLite database for every test so tests are fully
isolated and never touch the real ``app.db``.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.models import Job, Application

# The test engine — in-memory SQLite
_test_engine = None


def _get_test_engine():
    global _test_engine
    if _test_engine is None:
        _test_engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
        )
    return _test_engine


@pytest.fixture(autouse=True)
def _reset_tables():
    """Recreate all tables before each test for full isolation."""
    engine = _get_test_engine()
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    # Sessions are closed by fixtures; engine persists across the module


@pytest.fixture(name="session")
def fixture_session():
    """Yield a session bound to the test engine."""
    with Session(_get_test_engine()) as session:
        yield session


@pytest.fixture(name="client")
def fixture_client():
    """TestClient with the DB dependency overridden to use in-memory SQLite."""
    # Patch the engine used by the real get_session dependency
    import app.db.database as db_mod
    original_engine = db_mod.engine
    db_mod.engine = _get_test_engine()

    # Redefine get_session to use patched engine
    from app.db.database import get_session
    from app.main import app

    def _test_session():
        with Session(_get_test_engine()) as session:
            yield session

    app.dependency_overrides[get_session] = _test_session

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()
    db_mod.engine = original_engine


@pytest.fixture(name="sample_job")
def fixture_sample_job(session):
    """Insert and return a sample job."""
    job = Job(
        title="Python Developer",
        company="TestCorp",
        location="Remote",
        job_type="Full-time",
        description="Build backend services with Python and FastAPI.",
        requirements="3+ years Python, FastAPI, SQL, Docker.",
        salary_range="$100k - $130k",
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@pytest.fixture(name="sample_application")
def fixture_sample_application(session, sample_job):
    """Insert and return a sample application."""
    application = Application(
        job_id=sample_job.id,
        name="Jane Doe",
        email="jane@example.com",
        phone="+1234567890",
        resume_filename="jane_doe_resume.pdf",
        resume_text=(
            "Jane Doe\njane@example.com\n\nSenior Python Developer with 5 years "
            "of experience building production APIs with FastAPI and Django. "
            "Proficient in PostgreSQL, Docker, and AWS. BS in Computer Science."
        ),
    )
    session.add(application)
    sample_job.applications_count += 1
    session.add(sample_job)
    session.commit()
    session.refresh(application)
    return application
