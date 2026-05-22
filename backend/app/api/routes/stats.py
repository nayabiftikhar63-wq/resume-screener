"""Aggregate platform statistics for the admin dashboard."""

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.api.deps import get_session
from app.models import Application, Job

router = APIRouter(tags=["stats"])


@router.get("/api/stats")
async def get_stats(session: Session = Depends(get_session)):
    """Get overall platform statistics (Admin dashboard)."""
    total_jobs = session.exec(select(func.count()).select_from(Job)).one()
    total_apps = session.exec(select(func.count()).select_from(Application)).one()
    screened_apps = session.exec(
        select(func.count())
        .select_from(Application)
        .where(Application.screened == True)  # noqa: E712
    ).one()

    avg_score = 0
    if screened_apps:
        avg = session.exec(
            select(func.avg(Application.ai_score)).where(
                Application.screened == True  # noqa: E712
            )
        ).one()
        avg_score = round(avg or 0, 1)

    return {
        "total_jobs": total_jobs,
        "total_applications": total_apps,
        "screened_applications": screened_apps,
        "average_score": avg_score,
    }
