"""
Gemini AI Service for Resume Screening and Email Drafting.
Uses Google's latest Gemini 2.5 Flash model.
"""

import json
import os
import re
from datetime import date

from dotenv import load_dotenv
from google import genai

from app.core.paths import ENV_FILE

# Load .env from the backend directory.
load_dotenv(ENV_FILE)

# ─── Gemini Client Setup ─────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash-lite"

_client = None


def _get_client():
    """Lazily initialise the Gemini client so the server can start without a key."""
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
        if not key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. "
                "Run: export GEMINI_API_KEY='your-key-here' and restart the server."
            )
        _client = genai.Client(api_key=key)
    return _client


def screen_resume(
    resume_text: str,
    job_title: str,
    job_description: str,
    job_requirements: str,
) -> dict:
    """Screen a resume against a job description using Gemini.

    Returns a structured analysis with: score (0-100), summary, strengths,
    weaknesses, recommendation.
    """
    prompt = f"""
You are an expert AI recruiter and resume screener. Analyze the following resume against 
the job posting and provide a detailed, fair, and objective assessment.

IMPORTANT: Today's date is {date.today().strftime('%B %d, %Y')}. Use this as the reference 
point when evaluating dates on the resume (e.g. work experience, education, certifications).

═══════════════════════════════════════
JOB POSTING
═══════════════════════════════════════
Title: {job_title}

Description:
{job_description}

Requirements:
{job_requirements}

═══════════════════════════════════════
CANDIDATE RESUME
═══════════════════════════════════════
{resume_text}

═══════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════
Evaluate the resume against the job requirements and respond ONLY with a valid JSON object 
(no markdown fencing, no extra text) with EXACTLY these keys:

{{
  "score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "recommendation": "<one of: Strong Hire | Hire | Maybe | No Hire>"
}}

Scoring guide:
- 90-100: Exceptional match, exceeds all requirements
- 75-89: Strong match, meets most requirements
- 60-74: Moderate match, meets some requirements
- 40-59: Weak match, significant gaps
- 0-39: Poor match, does not meet requirements
"""

    try:
        response = _get_client().models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        raw = response.text.strip()

        # Strip markdown code fences if present.
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)

        result["score"] = max(0, min(100, int(result.get("score", 0))))
        result["summary"] = str(result.get("summary", "No summary available."))
        result["strengths"] = list(result.get("strengths", []))[:5]
        result["weaknesses"] = list(result.get("weaknesses", []))[:5]
        result["recommendation"] = str(result.get("recommendation", "No Hire"))

        return result

    except json.JSONDecodeError:
        return {
            "score": 0,
            "summary": f"AI analysis could not be parsed. Raw response: {raw[:200]}",
            "strengths": [],
            "weaknesses": ["Could not parse AI response"],
            "recommendation": "Error",
        }
    except Exception as e:
        return {
            "score": 0,
            "summary": f"AI screening failed: {str(e)}",
            "strengths": [],
            "weaknesses": ["AI service error"],
            "recommendation": "Error",
        }


# ─── Candidate Email Drafting ────────────────────────────────────

_EMAIL_TONE_INSTRUCTIONS = {
    "interview": (
        "Tone: warm, enthusiastic, congratulatory. The candidate has impressed "
        "the screening team and is being invited to the NEXT STEP (typically "
        "a recruiter call or first interview). Mention one or two SPECIFIC "
        "strengths from the analysis that stood out. Do NOT mention a score, "
        "ranking, or that AI was used. Ask the candidate to reply with their "
        "availability for the next week. Keep it under 150 words."
    ),
    "offer": (
        "Tone: warm, formal, celebratory. The candidate is being told that the "
        "team would like to extend an offer; full details (compensation, start "
        "date, etc.) will follow in a separate document. Reference one specific "
        "strength from the analysis. Do NOT invent numbers. Ask them to reply "
        "to confirm interest. Keep it under 150 words."
    ),
    "decline": (
        "Tone: kind, respectful, encouraging. The candidate will NOT be moving "
        "forward for this particular role. Thank them sincerely for their time "
        "and application. Do NOT enumerate weaknesses, give feedback, or mention "
        "any AI score. Wish them well and invite them to apply to future roles. "
        "Keep it under 120 words."
    ),
}


def draft_candidate_email(
    *,
    kind: str,
    candidate_name: str,
    job_title: str,
    job_company: str,
    job_description: str,
    ai_summary: str,
    ai_strengths: list[str],
    ai_recommendation: str,
) -> dict:
    """Generate a personalised candidate email draft.

    ``kind`` must be one of: ``"interview"`` | ``"offer"`` | ``"decline"``.
    Returns ``{"subject": str, "body": str, "kind": str}``.
    """
    tone = _EMAIL_TONE_INSTRUCTIONS.get(kind, _EMAIL_TONE_INSTRUCTIONS["interview"])
    strengths_block = (
        "\n".join(f"- {s}" for s in (ai_strengths or [])) or "(none recorded)"
    )

    prompt = f"""
You are a thoughtful technical recruiter drafting an email to a job candidate
on behalf of the hiring team. Write a personalised, professional email.

═══════════════════════════════════════
CONTEXT
═══════════════════════════════════════
Candidate name: {candidate_name}
Role: {job_title} at {job_company}
Job description: {job_description}

Internal screening summary (do NOT quote verbatim, use for personalisation only):
{ai_summary}

Candidate strengths the team noted:
{strengths_block}

Internal recommendation (do NOT reveal): {ai_recommendation}

═══════════════════════════════════════
EMAIL TYPE
═══════════════════════════════════════
{tone}

═══════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════
Respond ONLY with a valid JSON object (no markdown fencing, no extra text)
with EXACTLY these keys:

{{
  "subject": "<short subject line, no emojis>",
  "body": "<plain-text email body, no markdown, no HTML, use real newlines>"
}}

The body MUST:
- Start with "Hi {candidate_name}," (or "Dear {candidate_name},")
- End with a sign-off like "Best,\\nThe {job_company} Team"
- Use only plain text and real line breaks (no asterisks, no markdown)
- Never mention this is AI-generated, never reveal the internal score or recommendation
- Sound like it was written by a human recruiter
"""

    try:
        response = _get_client().models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        raw = response.text.strip()

        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)
        return {
            "subject": str(result.get("subject", "Update on your application")).strip(),
            "body": str(result.get("body", "")).strip(),
            "kind": kind,
        }

    except json.JSONDecodeError:
        return {
            "subject": "Update on your application",
            "body": (
                "AI email drafting could not be parsed. Raw response:\n\n"
                f"{raw[:400]}"
            ),
            "kind": kind,
            "error": "parse_error",
        }
    except Exception as e:
        return {
            "subject": "Update on your application",
            "body": f"AI email drafting failed: {e}",
            "kind": kind,
            "error": "service_error",
        }
