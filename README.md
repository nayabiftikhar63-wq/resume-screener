# 🧠 AI Resume Screener

> An intelligent resume screening platform powered by **Google Gemini 2.5 Flash** that evaluates candidate resumes against job descriptions, ranks applicants, and even drafts personalised candidate emails — instantly, fairly, and at scale.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![SQLModel](https://img.shields.io/badge/SQLModel-SQLite-336791?style=flat&logo=sqlite&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat&logo=vite&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI-4285F4?style=flat&logo=google&logoColor=white)

---

## 📌 Problem Statement

Manual resume screening is one of the most time-consuming tasks in recruitment. Recruiters spend an average of **6–7 seconds per resume**, leading to:

- ❌ Inconsistent evaluations across candidates
- ❌ Human bias influencing decisions
- ❌ Qualified candidates being overlooked
- ❌ Hours wasted on clearly unqualified applications

**Our Solution:** An AI-powered resume screener that uses Google's Gemini 2.5 Flash LLM to analyze resumes against job descriptions, produce structured fair evaluations, rank candidates, and even draft personalised follow-up emails for the top picks.

---

## ✨ Features

### 📋 For Candidates (Job Portal)
- Browse all open job positions (8 demo jobs seeded out of the box)
- View detailed job descriptions, requirements, and salary ranges
- Upload resume (PDF) with basic contact information
- Drag-and-drop file upload with type/size validation
- Instant success confirmation after submission

### 🛡️ For Admins (Admin Portal)
- **Dashboard** with real-time statistics (total jobs, applications, screened, avg. score)
- **Create / Delete** job postings with full descriptions and requirements
- **Sortable, ranked applications table** — screened candidates float to the top, ordered by AI score
- **🤖 AI Screen** — one-click to screen all unscreened resumes for a job
- **🔄 Re-screen all** — re-run Gemini on every application for a job (useful after editing the description); confirmation prompt prevents accidental spend
- **🔄 Re-screen this resume** — same idea, but per-candidate from the detail modal
- **📧 Draft email** — generate a personalised candidate-facing email in seconds (see below)
- **Detailed candidate view** — score, recommendation, summary, ranked strengths and weaknesses

### 🤖 AI Screening — Agentic Pipeline (Gemini 2.5 Flash)

Screening uses a **3-step agentic pipeline** that mirrors how a real recruiter
evaluates a candidate. Each step is a focused LLM call with its own prompt and
structured JSON output:

```
Resume PDF
    │
    ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  1. Extract      │────▶│  2. Match        │────▶│  3. Decide       │
│  Agent           │     │  Agent           │     │  Agent           │
│                  │     │                  │     │                  │
│  Parse skills,   │     │  Compare against │     │  Final score,    │
│  experience,     │     │  job reqs, score │     │  recommendation, │
│  education from  │     │  by category     │     │  strengths &     │
│  raw resume text │     │  (skills, exp,   │     │  weaknesses      │
│                  │     │  education)      │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

**Why an agentic pipeline instead of a single prompt?**
- Each agent has a **narrow, focused task** → fewer hallucinations
- **Intermediate outputs are inspectable** — the extracted profile and match
  analysis are stored in `pipeline_trace` for full auditability
- Individual steps can be **retried or swapped** without affecting others
- The Match Agent produces **category-level scores** (skills, experience,
  education) that give recruiters more granular insight

**Pipeline output includes:**
  - **Score** (0–100)
  - **Summary** (2–3 sentence assessment)
  - **Strengths** (top 3–5, used to personalise emails)
  - **Weaknesses** (top 2–3)
  - **Recommendation** (Strong Hire / Hire / Maybe / No Hire)
  - **Pipeline Trace** — extracted profile + match analysis for transparency

The pipeline is the default mode. Pass `?pipeline=false` to any screening
endpoint to fall back to the original single-prompt mode.

All results are persisted to SQLite so they survive server restarts.

### 📧 AI-Drafted Candidate Emails (Gemini 2.5 Flash)
After an application has been screened, admins can generate a personalised email
draft inline in the candidate detail modal. Powered by a separate Gemini prompt
that references the candidate's recorded strengths but never reveals the score,
ranking, or that AI was used.

Three tones are available, each with its own dedicated prompt:

| Tone | When to use | What the email contains |
|------|-------------|-------------------------|
| **Next step** | Strong / Hire / Maybe | Warm congratulations + invite to next interview round, references one or two specific strengths, asks for next-week availability |
| **Offer** | Final selection | Formal congratulations + signals an offer is coming, references one strength, asks them to confirm interest |
| **Decline** | No Hire | Kind, encouraging rejection that thanks them and invites future applications — no feedback, no scores |

Convenience features:
- **Smart default tone** — picks "decline" if the recommendation contains "No Hire", otherwise "interview"
- **Editable subject + body** — tweak the draft before copying
- **📋 Copy subject / Copy body** — one-click clipboard with toast confirmation
- **🔄 Regenerate** — re-roll the same tone for a different phrasing
- **Switch tones** — clicking "Next step" / "Offer" / "Decline" re-runs Gemini in that tone

---

## 🏗️ Architecture

```
Frontend (React + Vite SPA)          Backend (FastAPI + SQLModel + SQLite)
┌──────────────────────────┐         ┌────────────────────────────────────┐
│  /          → JobsList   │────────▶│  GET    /api/jobs                  │
│  /apply/:id → Apply      │────────▶│  POST   /api/jobs/:id/apply        │
│  /admin     → Admin      │────────▶│  POST   /api/jobs/:id/screen       │
│                          │────────▶│  POST   /api/applications/:id/...  │
│  Vite dev server (5173)  │         │            screen | draft-email    │
│  proxies /api → :8000    │         │                                    │
└──────────────────────────┘         │  app/services/gemini.py            │
                                     │  ┌──────────────────────────────┐  │
                                     │  │ Gemini 2.5 Flash             │  │
                                     │  │ • screen_resume()            │  │
                                     │  │ • draft_candidate_email()    │  │
                                     │  └──────────────────────────────┘  │
                                     │                                    │
                                     │  app.db ← jobs, applications,      │
                                     │           screening + email state  │
                                     │  uploads/ ← raw PDF files          │
                                     └────────────────────────────────────┘
```

In **development**, the Vite dev server (port 5173) proxies `/api/*` calls
to the FastAPI backend (port 8000). In **production**, `npm run build`
produces `frontend/dist/`, which FastAPI automatically serves on the same
origin — no separate web server needed.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ (for the React/Vite frontend)
- Google Gemini API Key ([Get one here](https://aistudio.google.com/apikey))

### Quick Start (Makefile)

The repo ships with a Makefile that automates the common workflows:

```bash
git clone <repository-url>
cd resume-screener
export GEMINI_API_KEY="your-api-key-here"

make install     # create venv, install Python + Node deps
make dev         # run FastAPI (:8000) + Vite (:5173) concurrently
# or for production:
make run         # build SPA and serve it from FastAPI on :8000
```

Run `make help` to list every target. Useful overrides:
`make dev BACKEND_PORT=9000`, `make clean` to wipe `venv/`, `node_modules/`, and `dist/`.

### Docker

A multi-stage Docker build (Node for the React SPA, Python for the backend)
serves the entire app from a single container:

```bash
# Set your API key in backend/.env, then:
make docker-up       # build + start on http://localhost:8000
make docker-logs     # follow logs
make docker-down     # stop
```

The Dockerfile builds the React SPA in a Node stage, copies the output into
the Python stage, and serves both the API and the SPA from FastAPI on port 8000.
Health checks, auto-restart, and named volumes for uploads and the SQLite DB
are included.

### Running Tests

```bash
make test
# or manually:
cd backend && python3 -m pytest tests/ -v
```

**27 tests** cover:
- **API integration tests** — endpoint routing, validation, error responses
- **Model tests** — schema defaults, foreign keys, screening field persistence
- **Pipeline tests** — all 3 agent steps mocked, error handling, JSON parsing, score clamping

### Persistence

Jobs, applications, and Gemini screening results are stored in a SQLite file
at `backend/app.db`, which is created automatically on first boot and seeded
with **8 demo jobs** spanning engineering, ML, design, DevOps, mobile, security,
and product roles. Resume PDFs are written to `backend/uploads/`.

- The DB **survives server restarts** — candidate applications, screening
  results, and AI summaries are all persisted.
- Seeding is **idempotent**: each demo job is matched by `(title, company)` and
  only inserted if missing, so admin-created jobs are never touched on boot.
- To permanently retire a demo job, remove its entry from `DEMO_JOBS` in
  `backend/app/services/seed.py` (otherwise it'll re-seed on next start).
- To wipe all state and start fresh: `rm backend/app.db backend/uploads/*.pdf`.

Email drafts are **not** persisted — they're regenerated on demand from the
stored screening result so they always reflect the latest AI analysis.

### Manual Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd resume-screener

# 2. Set up the backend (FastAPI)
python3 -m venv venv
source venv/bin/activate            # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
export GEMINI_API_KEY="your-api-key-here"

# 3. Set up the frontend (React + Vite)
cd frontend
npm install
cd ..
```

### Running in Development

Run the backend and the Vite dev server in two terminals:

```bash
# Terminal 1 – FastAPI (port 8000)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 – Vite dev server (port 5173, proxies /api to :8000)
cd frontend
npm run dev
```

### Building for Production

Build the SPA once, then FastAPI will serve it on the same origin:

```bash
cd frontend && npm run build && cd ..
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Access the Application
| Page | Dev URL | Production URL |
|------|---------|----------------|
| **Job Listings** (Candidate) | [http://localhost:5173](http://localhost:5173) | http://localhost:8000 |
| **Apply** | http://localhost:5173/apply/`:jobId` | http://localhost:8000/apply/`:jobId` |
| **Admin Portal** | [http://localhost:5173/admin](http://localhost:5173/admin) | http://localhost:8000/admin |
| **API Docs** (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) | http://localhost:8000/docs |

---

## 📁 Project Structure

```
resume-screener/
├── backend/
│   ├── app/                         # FastAPI application package
│   │   ├── main.py                  # App entry: lifespan, CORS, router wiring, SPA mount
│   │   ├── api/
│   │   │   ├── deps.py              # Shared dependencies (DB session)
│   │   │   └── routes/
│   │   │       ├── jobs.py          # /api/jobs CRUD
│   │   │       ├── applications.py  # /apply + list applications
│   │   │       ├── screening.py     # Bulk + single AI screening
│   │   │       ├── emails.py        # AI email drafting
│   │   │       └── stats.py         # /api/stats
│   │   ├── core/
│   │   │   └── paths.py             # Centralised filesystem paths
│   │   ├── db/
│   │   │   └── database.py          # SQLite engine + session dependency
│   │   ├── models/
│   │   │   └── schemas.py           # SQLModel ORM / Pydantic schemas
│   │   └── services/
│   │       ├── gemini.py            # Gemini AI integration (single-prompt mode)
│   │       ├── screening_pipeline.py # Agentic 3-step pipeline (Extract → Match → Decide)
│   │       └── seed.py              # DEMO_JOBS + idempotent seeding
│   ├── tests/                       # 27 unit + integration tests
│   │   ├── test_api.py              # API endpoint integration tests
│   │   ├── test_models.py           # Data model tests
│   │   └── test_screening.py        # Agentic pipeline tests (mocked Gemini)
│   ├── requirements.txt             # Python dependencies
│   ├── app.db                       # SQLite database (created on first run)
│   └── uploads/                     # Stored resume PDFs
├── frontend/
│   ├── index.html                   # Vite HTML shell
│   ├── package.json                 # Node dependencies / scripts
│   ├── vite.config.js               # Vite config (incl. /api dev proxy)
│   └── src/
│       ├── main.jsx                 # React entry point
│       ├── App.jsx                  # Router & layout
│       ├── api.js                   # Fetch wrapper for backend
│       ├── index.css                # Dark glassmorphic design system
│       ├── components/              # Navbar, Modal, Loading, ToastProvider
│       ├── pages/                   # JobsList, Apply, Admin (incl. email drafting)
│       └── utils/                   # Score / recommendation helpers
├── Makefile                         # install / dev / build / run / test / docker targets
├── Dockerfile                       # Multi-stage build (Node SPA + Python backend)
├── docker-compose.yml               # One-command deployment with health checks
├── .dockerignore                    # Excluded files from Docker build
├── GEMINI.md                        # AI checkpoints & integration details
└── README.md                        # This file
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/jobs` | List all jobs |
| `GET` | `/api/jobs/{id}` | Get job details |
| `POST` | `/api/jobs` | Create a job (admin) |
| `DELETE` | `/api/jobs/{id}` | Delete a job and cascade-delete its applications (admin) |
| `POST` | `/api/jobs/{id}/apply` | Submit an application (multipart form with PDF) |
| `GET` | `/api/jobs/{id}/applications` | List applications for a job (admin) |
| `POST` | `/api/jobs/{id}/screen` | AI-screen unscreened resumes — add `?force=true` to **re-screen all**, `?pipeline=false` for single-prompt mode (admin) |
| `POST` | `/api/applications/{id}/screen` | AI-screen a single resume — add `?pipeline=false` for single-prompt mode (admin) |
| `POST` | `/api/applications/{id}/draft-email` | Draft a candidate-facing email. Query param `kind=interview\|offer\|decline` (default: `interview`). Requires the application to be screened first. (admin) |
| `GET` | `/api/stats` | Platform statistics (admin) |

Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python 3.10+) |
| **AI / LLM** | Google Gemini 2.5 Flash (`gemini-2.5-flash-lite` by default) |
| **Gemini SDK** | `google-genai` |
| **PDF Parsing** | PyPDF2 |
| **Database** | SQLite via SQLModel (file: `backend/app.db`) |
| **File storage** | Local filesystem (`backend/uploads/`) |
| **Frontend** | React 18 + Vite 5 |
| **Routing** | React Router v6 |
| **Styling** | Custom dark glassmorphic design system (single CSS file) |
| **Testing** | pytest + httpx (27 tests, mocked Gemini calls) |
| **Containerisation** | Docker multi-stage build + Docker Compose |
| **Build tooling** | `make` for dev/run/test/docker workflows |

---

## 📊 AI Scoring Rubric

| Score | Rating | Meaning |
|-------|--------|---------|
| 90–100 | 🟢 Exceptional | Exceeds all requirements |
| 75–89 | 🟢 Strong | Meets most requirements |
| 60–74 | 🟡 Moderate | Meets some requirements |
| 40–59 | 🟠 Weak | Significant gaps |
| 0–39 | 🔴 Poor | Does not meet requirements |

---

## 🛠️ Troubleshooting

### `ERROR: [Errno 48] Address already in use` when running `make dev`
A previous uvicorn is still holding port 8000 (commonly because its parent
terminal was closed but the process was orphaned). Kill it and retry:

```bash
pkill -9 -f "uvicorn app.main:app"
make dev
```

### Vite logs `[vite] http proxy error: /api/* AggregateError [ETIMEDOUT]`
On macOS, `localhost` resolves to **both** `::1` (IPv6) and `127.0.0.1`. Node
18+ may try IPv6 first, but `uvicorn --host 0.0.0.0` only binds IPv4 — so the
proxy connection times out. This repo's `vite.config.js` already pins the
proxy target to `http://127.0.0.1:8000` to avoid this. If you change it back
to `localhost` and see timeouts, that's why.

### Gemini returns `404 NOT_FOUND: models/... is not found`
The model name in `backend/app/services/gemini.py` (`MODEL_NAME`) is invalid or
unavailable to your API key. The default is `gemini-2.5-flash-lite`; valid
alternatives include `gemini-2.5-flash` and `gemini-1.5-flash`. Check what
your key has access to at [Google AI Studio](https://aistudio.google.com).

### `GEMINI_API_KEY environment variable is not set`
The backend starts fine without a key, but any screening or email-drafting
call will fail with this error. Set the key before running:

```bash
export GEMINI_API_KEY="your-key-here"
# or put it in backend/.env
```

### Deleted a demo job but it came back after restart
Demo job seeding is idempotent and topped-up on every boot. To permanently
retire one, remove its entry from `DEMO_JOBS` in `backend/app/services/seed.py`.

### Want a completely fresh database
```bash
rm backend/app.db backend/uploads/*.pdf
```
Next boot will recreate the schema and re-seed the 8 demo jobs.

---

## 📄 License

This project is developed as a prototype/proof-of-concept for demonstrating AI-powered workflows in recruitment.

---

