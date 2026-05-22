"""CRUD endpoints for job postings."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_session
from app.models import Application, Job, JobCreate

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
async def list_jobs(session: Session = Depends(get_session)):
    """List all active job postings."""
    return session.exec(select(Job)).all()


@router.get("/{job_id}")
async def get_job(job_id: str, session: Session = Depends(get_session)):
    """Get a specific job by ID."""
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("")
async def create_job(
    job_data: JobCreate,
    session: Session = Depends(get_session),
):
    """Create a new job posting (Admin)."""
    job = Job(**job_data.model_dump())
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.delete("/{job_id}")
async def delete_job(job_id: str, session: Session = Depends(get_session)):
    """Delete a job posting and all of its applications (Admin)."""
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Remove related applications first to satisfy the foreign-key constraint.
    related = session.exec(
        select(Application).where(Application.job_id == job_id)
    ).all()
    for app_row in related:
        session.delete(app_row)

    session.delete(job)
    session.commit()
    return {"message": "Job deleted successfully"}
