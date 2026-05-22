"""
Data models for the AI Resume Screener.

Uses SQLModel so the same classes act as both Pydantic schemas (for FastAPI
request/response validation) and SQLAlchemy ORM tables (persisted to SQLite).
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


# ─── Job ─────────────────────────────────────────────────────────


class JobBase(SQLModel):
    """Fields shared between the request body and the persisted row."""

    title: str
    company: str
    location: str
    job_type: str  # Full-time, Part-time, Contract, Remote
    description: str
    requirements: str
    salary_range: Optional[str] = None


class JobCreate(JobBase):
    """Schema for `POST /api/jobs` (admin)."""


class Job(JobBase, table=True):
    """Persisted job posting."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    # Denormalised counter — kept in sync by the apply / delete handlers so
    # the admin sidebar can render counts without a JOIN.
    applications_count: int = 0


# ─── Application ─────────────────────────────────────────────────


class ApplicationBase(SQLModel):
    """Fields captured at submission time."""

    job_id: str = Field(foreign_key="job.id", index=True)
    name: str
    email: str
    phone: Optional[str] = None
    resume_filename: str
    resume_text: str = ""


class ApplicationCreate(SQLModel):
    """Schema for the multipart `POST /api/jobs/{id}/apply` form body."""

    name: str
    email: str
    phone: Optional[str] = None


class Application(ApplicationBase, table=True):
    """Persisted application + Gemini screening results."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    ai_score: Optional[float] = None
    ai_summary: Optional[str] = None
    # SQLite has no native array type, so we serialise these as JSON.
    ai_strengths: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    ai_weaknesses: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    ai_recommendation: Optional[str] = None
    # Agentic pipeline intermediate outputs (Extract → Match → Decide trace).
    pipeline_trace: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    screened: bool = False
    applied_at: str = Field(default_factory=lambda: datetime.now().isoformat())
