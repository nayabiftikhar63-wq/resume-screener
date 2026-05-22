"""AI screening endpoints (bulk + single).

Supports two modes:
  • ``pipeline=false`` (default) — single-prompt screening via Gemini
  • ``pipeline=true`` — 3-step agentic pipeline (Extract → Match → Decide)

The agentic pipeline produces richer, more auditable results with
intermediate outputs stored in ``pipeline_trace``.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_session
from app.models import Application, Job
from app.services.gemini import screen_resume
from app.services.screening_pipeline import run_screening_pipeline

router = APIRouter(tags=["screening"])


def _apply_screening_result(application: Application, ai_result: dict) -> None:
    """Copy a Gemini result onto the Application row (in-place)."""
    application.ai_score = ai_result["score"]
    application.ai_summary = ai_result["summary"]
    application.ai_strengths = ai_result["strengths"]
    application.ai_weaknesses = ai_result["weaknesses"]
    application.ai_recommendation = ai_result["recommendation"]
    application.pipeline_trace = ai_result.get("pipeline_trace")
    application.screened = True


def _screen(application: Application, job: Job, use_pipeline: bool) -> dict:
    """Run screening via the selected mode."""
    if use_pipeline:
        return run_screening_pipeline(
            resume_text=application.resume_text,
            job_title=job.title,
            job_description=job.description,
            job_requirements=job.requirements,
        )
    return screen_resume(
        resume_text=application.resume_text,
        job_title=job.title,
        job_description=job.description,
        job_requirements=job.requirements,
    )


@router.post("/api/jobs/{job_id}/screen")
async def screen_all_resumes(
    job_id: str,
    force: bool = False,
    pipeline: bool = True,
    session: Session = Depends(get_session),
):
    """Screen resumes for a job using Gemini AI.

    By default, only applications that haven't been screened yet are
    processed. Pass ``?force=true`` to re-screen every application for the
    job (useful after editing the job description or requirements).

    Pass ``?pipeline=true`` (default) to use the multi-step agentic
    pipeline (Extract → Match → Decide). Pass ``?pipeline=false`` for the
    single-prompt mode.
    """
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    stmt = select(Application).where(Application.job_id == job_id)
    if not force:
        stmt = stmt.where(Application.screened == False)  # noqa: E712

    targets = session.exec(stmt).all()

    if not targets:
        detail = (
            "No applications to re-screen"
            if force
            else "No unscreened applications found"
        )
        raise HTTPException(status_code=400, detail=detail)

    for application in targets:
        ai_result = _screen(application, job, use_pipeline=pipeline)
        _apply_screening_result(application, ai_result)
        session.add(application)

    session.commit()
    for application in targets:
        session.refresh(application)
    return targets


@router.post("/api/applications/{app_id}/screen")
async def screen_single_resume(
    app_id: str,
    pipeline: bool = True,
    session: Session = Depends(get_session),
):
    """Screen a single application using Gemini AI.

    Pass ``?pipeline=true`` (default) for the agentic pipeline,
    or ``?pipeline=false`` for single-prompt mode.
    """
    application = session.get(Application, app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    job = session.get(Job, application.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Associated job not found")

    ai_result = _screen(application, job, use_pipeline=pipeline)
    _apply_screening_result(application, ai_result)

    session.add(application)
    session.commit()
    session.refresh(application)
    return application
