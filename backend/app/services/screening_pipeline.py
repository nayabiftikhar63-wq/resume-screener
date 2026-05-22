"""
Agentic Screening Pipeline
===========================
A multi-step agent chain that mirrors how a real recruiter evaluates a
candidate — each step builds on the previous one's output:

  1. **Extract Agent** — Pulls structured data from the raw resume text
     (skills, experience years, education, certifications).
  2. **Match Agent** — Compares extracted data against job requirements
     and produces a scored breakdown by category.
  3. **Decide Agent** — Synthesises the match report into a final score,
     recommendation, summary, strengths, and weaknesses.
  4. **Email Agent** — (Optional) Drafts a personalised candidate email
     based on the decision output.

Each step is a focused, single-responsibility LLM call with its own prompt
and structured JSON output. This is more reliable and auditable than a
single monolithic prompt because:

  • Each agent has a narrow task → fewer hallucinations.
  • Intermediate outputs are inspectable (stored in ``pipeline_trace``).
  • Individual steps can be retried or swapped without affecting others.
"""

import json
import re
from datetime import date

from app.services.gemini import _get_client, MODEL_NAME


def _call_gemini(prompt: str) -> str:
    """Make a single Gemini API call and return the raw text response."""
    response = _get_client().models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text.strip()


def _parse_json(raw: str) -> dict:
    """Parse JSON from an LLM response, stripping markdown fences if present."""
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


# ─── Step 1: Extract Agent ────────────────────────────────────────


def extract_resume_data(resume_text: str) -> dict:
    """Extract structured data from raw resume text.

    Returns: {name, email, skills[], experience_years, education,
              certifications[], recent_role, summary}
    """
    prompt = f"""You are a precise data extraction agent. Extract structured information
from the following resume. Return ONLY valid JSON (no markdown fencing).

RESUME:
{resume_text}

IMPORTANT: Today's date is {date.today().strftime('%B %d, %Y')}.
Calculate experience_years by summing all work experience durations.

Return this exact JSON structure:
{{
  "name": "<full name>",
  "email": "<email if found, else null>",
  "skills": ["<skill1>", "<skill2>", ...],
  "experience_years": <number>,
  "education": "<highest degree and institution>",
  "certifications": ["<cert1>", ...],
  "recent_role": "<most recent job title at company>",
  "summary": "<1-sentence profile summary>"
}}"""

    try:
        raw = _call_gemini(prompt)
        data = _parse_json(raw)
        # Normalize
        data["skills"] = list(data.get("skills", []))
        data["experience_years"] = float(data.get("experience_years", 0))
        data["certifications"] = list(data.get("certifications", []))
        return data
    except Exception as e:
        return {
            "name": None,
            "email": None,
            "skills": [],
            "experience_years": 0,
            "education": None,
            "certifications": [],
            "recent_role": None,
            "summary": f"Extraction failed: {e}",
            "error": str(e),
        }


# ─── Step 2: Match Agent ─────────────────────────────────────────


def match_against_job(
    extracted: dict,
    job_title: str,
    job_description: str,
    job_requirements: str,
) -> dict:
    """Compare extracted resume data against job requirements.

    Returns: {skill_match, experience_match, education_match,
              overall_fit, matched_skills[], missing_skills[], analysis}
    """
    prompt = f"""You are a job-matching analysis agent. Compare the candidate profile below
against the job requirements and score each dimension.

CANDIDATE PROFILE:
- Skills: {', '.join(extracted.get('skills', []))}
- Experience: {extracted.get('experience_years', 0)} years
- Education: {extracted.get('education', 'Unknown')}
- Certifications: {', '.join(extracted.get('certifications', []))}
- Recent Role: {extracted.get('recent_role', 'Unknown')}
- Summary: {extracted.get('summary', '')}

JOB POSTING:
Title: {job_title}
Description: {job_description}
Requirements: {job_requirements}

Return ONLY valid JSON (no markdown fencing):
{{
  "skill_match": <0-100 score for skills alignment>,
  "experience_match": <0-100 score for experience level fit>,
  "education_match": <0-100 score for education fit>,
  "overall_fit": <0-100 weighted average>,
  "matched_skills": ["<skills the candidate has that match>"],
  "missing_skills": ["<required skills the candidate lacks>"],
  "analysis": "<2-3 sentence analysis of the match quality>"
}}"""

    try:
        raw = _call_gemini(prompt)
        data = _parse_json(raw)
        data["skill_match"] = max(0, min(100, int(data.get("skill_match", 0))))
        data["experience_match"] = max(0, min(100, int(data.get("experience_match", 0))))
        data["education_match"] = max(0, min(100, int(data.get("education_match", 0))))
        data["overall_fit"] = max(0, min(100, int(data.get("overall_fit", 0))))
        return data
    except Exception as e:
        return {
            "skill_match": 0,
            "experience_match": 0,
            "education_match": 0,
            "overall_fit": 0,
            "matched_skills": [],
            "missing_skills": [],
            "analysis": f"Matching failed: {e}",
            "error": str(e),
        }


# ─── Step 3: Decide Agent ────────────────────────────────────────


def make_decision(extracted: dict, match_result: dict) -> dict:
    """Synthesise extraction and match results into a final hiring decision.

    Returns the same schema as the original screen_resume() for backward
    compatibility: {score, summary, strengths[], weaknesses[], recommendation}
    """
    prompt = f"""You are a senior hiring decision agent. Based on the candidate analysis
and job match results below, make a final hiring recommendation.

CANDIDATE PROFILE:
- Name: {extracted.get('name', 'Unknown')}
- Experience: {extracted.get('experience_years', 0)} years
- Recent Role: {extracted.get('recent_role', 'Unknown')}
- Education: {extracted.get('education', 'Unknown')}

MATCH ANALYSIS:
- Skill Match: {match_result.get('skill_match', 0)}/100
- Experience Match: {match_result.get('experience_match', 0)}/100
- Education Match: {match_result.get('education_match', 0)}/100
- Overall Fit: {match_result.get('overall_fit', 0)}/100
- Matched Skills: {', '.join(match_result.get('matched_skills', []))}
- Missing Skills: {', '.join(match_result.get('missing_skills', []))}
- Analysis: {match_result.get('analysis', '')}

Return ONLY valid JSON (no markdown fencing):
{{
  "score": <integer 0-100, must be consistent with match scores>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "recommendation": "<one of: Strong Hire | Hire | Maybe | No Hire>"
}}

Scoring guide:
- 90-100: Exceptional match (Strong Hire)
- 75-89: Strong match (Hire)
- 60-74: Moderate match (Maybe)
- 40-59: Weak match (No Hire)
- 0-39: Poor match (No Hire)"""

    try:
        raw = _call_gemini(prompt)
        data = _parse_json(raw)
        data["score"] = max(0, min(100, int(data.get("score", 0))))
        data["strengths"] = list(data.get("strengths", []))[:5]
        data["weaknesses"] = list(data.get("weaknesses", []))[:5]
        data["summary"] = str(data.get("summary", "No summary available."))
        data["recommendation"] = str(data.get("recommendation", "No Hire"))
        return data
    except Exception as e:
        return {
            "score": 0,
            "summary": f"Decision failed: {e}",
            "strengths": [],
            "weaknesses": ["Pipeline error"],
            "recommendation": "Error",
            "error": str(e),
        }


# ─── Orchestrator ─────────────────────────────────────────────────


def run_screening_pipeline(
    resume_text: str,
    job_title: str,
    job_description: str,
    job_requirements: str,
) -> dict:
    """Execute the full 3-step agentic screening pipeline.

    Returns the final decision dict (same schema as gemini.screen_resume)
    plus a ``pipeline_trace`` field with intermediate agent outputs for
    auditability.
    """
    # Step 1: Extract structured data from resume
    extracted = extract_resume_data(resume_text)

    # Step 2: Match against job requirements
    match_result = match_against_job(
        extracted, job_title, job_description, job_requirements
    )

    # Step 3: Make final decision
    decision = make_decision(extracted, match_result)

    # Attach the full trace for transparency
    decision["pipeline_trace"] = {
        "extracted_profile": extracted,
        "match_analysis": match_result,
    }

    return decision
