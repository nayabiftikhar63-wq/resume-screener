"""AI-drafted candidate email endpoint."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_session
from app.models import Application, Job
from app.services.gemini import draft_candidate_email

EmailKind = Literal["interview", "offer", "decline"]

router = APIRouter(prefix="/api/applications", tags=["emails"])


@router.post("/{app_id}/draft-email")
async def draft_application_email(
    app_id: str,
    kind: EmailKind = "interview",
    session: Session = Depends(get_session),
):
    """Use Gemini to draft a personalised candidate-facing email.

    ``kind`` controls the tone:
      • ``interview`` — congratulate + invite to next round (default)
      • ``offer``     — extend an offer; details will follow
      • ``decline``   — polite rejection
    """
    application = session.get(Application, app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if not application.screened:
        raise HTTPException(
            status_code=400,
            detail="Screen the application first so the email can be personalised.",
        )

    job = session.get(Job, application.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Associated job not found")

    return draft_candidate_email(
        kind=kind,
        candidate_name=application.name,
        job_title=job.title,
        job_company=job.company,
        job_description=job.description,
        ai_summary=application.ai_summary or "",
        ai_strengths=application.ai_strengths or [],
        ai_recommendation=application.ai_recommendation or "",
    )
