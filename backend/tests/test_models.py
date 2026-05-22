"""Tests for data models and database operations."""

from sqlmodel import Session, select

from app.models import Job, Application


def test_create_job_model(session):
    """Job model generates UUID and timestamp on creation."""
    job = Job(
        title="Tester",
        company="QA Inc",
        location="Remote",
        job_type="Full-time",
        description="Test stuff.",
        requirements="pytest.",
    )
    session.add(job)
    session.commit()
    session.refresh(job)

    assert job.id is not None
    assert len(job.id) == 36  # UUID format
    assert job.created_at is not None
    assert job.applications_count == 0


def test_create_application_model(session, sample_job):
    """Application model stores resume text and AI fields default to None."""
    app = Application(
        job_id=sample_job.id,
        name="Test User",
        email="test@test.com",
        resume_filename="test.pdf",
        resume_text="Some resume text.",
    )
    session.add(app)
    session.commit()
    session.refresh(app)

    assert app.id is not None
    assert app.ai_score is None
    assert app.ai_summary is None
    assert app.ai_strengths is None
    assert app.ai_weaknesses is None
    assert app.ai_recommendation is None
    assert app.pipeline_trace is None
    assert app.screened is False


def test_application_foreign_key(session, sample_job):
    """Application references the correct job via foreign key."""
    app = Application(
        job_id=sample_job.id,
        name="FK Test",
        email="fk@test.com",
        resume_filename="fk.pdf",
    )
    session.add(app)
    session.commit()

    fetched = session.exec(
        select(Application).where(Application.job_id == sample_job.id)
    ).first()
    assert fetched is not None
    assert fetched.name == "FK Test"


def test_application_screening_fields(session, sample_application):
    """Screening results can be stored on the Application model."""
    sample_application.ai_score = 85.0
    sample_application.ai_summary = "Strong candidate."
    sample_application.ai_strengths = ["Python", "FastAPI"]
    sample_application.ai_weaknesses = ["No Docker"]
    sample_application.ai_recommendation = "Hire"
    sample_application.pipeline_trace = {
        "extracted_profile": {"skills": ["Python"]},
        "match_analysis": {"overall_fit": 85},
    }
    sample_application.screened = True

    session.add(sample_application)
    session.commit()
    session.refresh(sample_application)

    assert sample_application.ai_score == 85.0
    assert sample_application.ai_strengths == ["Python", "FastAPI"]
    assert sample_application.pipeline_trace["match_analysis"]["overall_fit"] == 85
    assert sample_application.screened is True
