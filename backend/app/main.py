"""
AI Resume Screener – FastAPI Application Entry Point
====================================================
Wires together:
  • SQLite + SQLModel persistence  (``app.db.database``)
  • Demo data seeding              (``app.services.seed``)
  • REST API routers               (``app.api.routes.*``)
  • Static SPA serving (production build under ``frontend/dist``)

In development:
  • Vite (``cd frontend && npm run dev``) serves the React SPA on :5173 and
    proxies ``/api/*`` to this process on :8000.

In production:
  • ``cd frontend && npm run build`` produces ``frontend/dist``; this app
    then serves the built assets on the same origin alongside the API.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import applications, emails, jobs, screening, stats
from app.core.paths import FRONTEND_DIST, UPLOAD_DIR
from app.db.database import init_db
from app.services.seed import seed_if_empty


@asynccontextmanager
async def lifespan(_app: FastAPI):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    seed_if_empty()
    yield


app = FastAPI(
    title="AI Resume Screener",
    description="Intelligent resume screening powered by Google Gemini 2.5 Flash",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS is permissive so the Vite dev server (default http://localhost:5173)
# can call the API directly even without the proxy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────
# Order matters only relative to the SPA mount below — every API route
# must be registered before the catch-all static mount.

app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(screening.router)
app.include_router(emails.router)
app.include_router(stats.router)


# ─── Serve React Build (production) ──────────────────────────────
# If the Vite build output exists, serve it under "/" with a SPA
# fallback so client-side routes like /apply/:jobId and /admin work.

if FRONTEND_DIST.is_dir():
    # ``html=True`` makes StaticFiles serve ``index.html`` on any unmatched
    # path so React Router can handle the route on the client.
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIST), html=True),
        name="spa",
    )
else:

    @app.get("/")
    async def root():
        """Friendly hint when the SPA hasn't been built yet."""
        return {
            "message": (
                "AI Resume Screener API is running. "
                "Start the React dev server (`cd frontend && npm run dev`) "
                "or run `npm run build` to serve the SPA from this origin."
            ),
            "docs": "/docs",
        }
