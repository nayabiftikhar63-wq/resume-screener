# 🤖 GEMINI.md – AI Resume Screener Checkpoints

> This document tracks the project checkpoints, Gemini AI integration details, and development milestones.

---

## 📌 Project Overview

| Item | Detail |
|------|--------|
| **Project** | AI Resume Screener |
| **LLM Used** | Google Gemini 3.5 Flash (`gemini-3.5-flash`) |
| **SDK** | `google-genai` (Python) |
| **Backend** | FastAPI (Python) |
| **Frontend** | Vanilla HTML / CSS / JavaScript |

---

## ✅ Checkpoint 1 – Problem Definition

**Business Problem:** Manual resume screening is time-consuming, inconsistent, and prone to human bias. Recruiters spend an average of 6–7 seconds per resume, often missing qualified candidates or passing through unqualified ones.

**AI Solution:** An AI-powered resume screening system that:
- Accepts job descriptions and candidate resumes (PDF)
- Uses Google Gemini 3.5 Flash to intelligently analyze each resume against job requirements
- Produces a structured evaluation: score (0–100), strengths, weaknesses, and hire recommendation
- Provides consistent, fair, and instant screening at scale

**Value Created:**
- ⏱️ Reduces screening time from minutes to seconds per resume
- 📊 Provides quantitative scoring for objective comparison
- 🎯 Highlights relevant strengths and gaps for each candidate
- ⚖️ Ensures consistent evaluation criteria across all applicants

---

## ✅ Checkpoint 2 – Architecture & Design

```
┌─────────────────────────────────────────────┐
│              Frontend (HTML/CSS/JS)          │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  Jobs     │  │  Apply   │  │  Admin    │  │
│  │  Listing  │  │  Page    │  │  Portal   │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  │
│       │              │              │         │
└───────┼──────────────┼──────────────┼─────────┘
        │              │              │
        ▼              ▼              ▼
┌─────────────────────────────────────────────┐
│           FastAPI Backend (REST API)         │
│  ┌─────────────┐  ┌────────────────────┐    │
│  │ Job CRUD    │  │  Application       │    │
│  │ Endpoints   │  │  Management        │    │
│  └─────────────┘  └────────┬───────────┘    │
│                            │                 │
│                   ┌────────▼───────────┐     │
│                   │  Gemini AI Service │     │
│                   │  (gemini-3.5-flash)│     │
│                   └────────────────────┘     │
└─────────────────────────────────────────────┘
```

---

## ✅ Checkpoint 3 – Gemini Integration

### Model Configuration
- **Model:** `gemini-3.5-flash` (latest GA, released May 19, 2026)
- **SDK:** `google-genai` Python client
- **Output Format:** Structured JSON (score, summary, strengths, weaknesses, recommendation)

### Prompt Engineering
The screening prompt:
1. Presents the full job description and requirements
2. Presents the extracted resume text
3. Requests a structured JSON evaluation with specific scoring rubric
4. Enforces a 0–100 scoring scale with defined thresholds

### Scoring Rubric
| Score Range | Meaning |
|-------------|---------|
| 90–100 | Exceptional match – exceeds all requirements |
| 75–89 | Strong match – meets most requirements |
| 60–74 | Moderate match – meets some requirements |
| 40–59 | Weak match – significant gaps |
| 0–39 | Poor match – does not meet requirements |

### Recommendation Categories
- **Strong Hire** – Exceptional candidate, fast-track interview
- **Hire** – Good candidate, proceed with interview
- **Maybe** – Borderline, needs further review
- **No Hire** – Does not meet minimum requirements

---

## ✅ Checkpoint 4 – Backend Implementation

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/jobs` | List all job postings |
| `GET` | `/api/jobs/{id}` | Get a specific job |
| `POST` | `/api/jobs` | Create a new job posting |
| `DELETE` | `/api/jobs/{id}` | Delete a job |
| `POST` | `/api/jobs/{id}/apply` | Submit application with PDF resume |
| `GET` | `/api/jobs/{id}/applications` | List all applications for a job |
| `POST` | `/api/jobs/{id}/screen` | Screen all unscreened resumes for a job |
| `POST` | `/api/applications/{id}/screen` | Screen a single resume |
| `GET` | `/api/stats` | Get platform statistics |

### Key Technical Decisions
- **In-memory storage** for prototype simplicity (no database setup required)
- **PyPDF2** for PDF text extraction
- **Structured JSON prompting** to ensure consistent AI output parsing
- **Error handling** with fallback responses if Gemini fails

---

## ✅ Checkpoint 5 – Frontend Implementation

### Pages
1. **Job Listings** (`index.html`) – Card grid of all open positions
2. **Apply Page** (`apply.html`) – Job details + application form with drag-and-drop PDF upload
3. **Admin Portal** (`admin.html`) – Stats dashboard, job management sidebar, applications table, AI screening controls

### Design System
- Dark glassmorphic theme with indigo accent palette
- Inter font family from Google Fonts
- Responsive grid layouts
- Micro-animations and hover effects
- Toast notifications for user feedback

---

## 🔄 Future Enhancements (Potential Checkpoints)
- [ ] Persistent database (PostgreSQL/MongoDB)
- [ ] User authentication for admin portal
- [ ] Batch resume upload
- [ ] Email notifications to candidates
- [ ] Resume comparison / ranking dashboard
- [ ] Export screening results as CSV/PDF
