"""Endpoints for submitting and listing applications."""

import io

import PyPDF2
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from app.api.deps import get_session
from app.core.paths import UPLOAD_DIR
from app.models import Application, Job

router = APIRouter(prefix="/api/jobs", tags=["applications"])

# Ensure the uploads directory exists at import time.
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{job_id}/apply")
async def apply_to_job(
    job_id: str,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    resume: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    """Submit a job application with a resume PDF."""
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    file_content = await resume.read()
    file_path = UPLOAD_DIR / f"{job_id}_{resume.filename}"
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Extract text for later AI screening; tolerate parser failures.
    resume_text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                resume_text += page_text + "\n"
    except Exception:
        resume_text = "[Could not extract text from PDF]"

    application = Application(
        job_id=job_id,
        name=name,
        email=email,
        phone=phone,
        resume_filename=resume.filename,
        resume_text=resume_text,
    )
    session.add(application)

    job.applications_count += 1
    session.add(job)

    session.commit()
    session.refresh(application)

    return {
        "message": "Application submitted successfully!",
        "application_id": application.id,
    }


@router.get("/{job_id}/applications")
async def list_applications(
    job_id: str,
    session: Session = Depends(get_session),
):
    """List all applications for a specific job (Admin)."""
    if not session.get(Job, job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return session.exec(
        select(Application).where(Application.job_id == job_id)
    ).all()
