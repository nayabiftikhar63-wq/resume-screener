"""Tests for the screening pipeline logic.

These tests mock the Gemini API calls so they run offline and for free.
They verify the pipeline orchestration, JSON parsing, and error handling.
"""

from unittest.mock import patch, MagicMock

from app.services.screening_pipeline import (
    extract_resume_data,
    match_against_job,
    make_decision,
    run_screening_pipeline,
)


MOCK_EXTRACT_RESPONSE = """{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
  "experience_years": 5,
  "education": "BS Computer Science, MIT",
  "certifications": ["AWS Solutions Architect"],
  "recent_role": "Senior Developer at TechCo",
  "summary": "Experienced Python developer with backend focus."
}"""

MOCK_MATCH_RESPONSE = """{
  "skill_match": 90,
  "experience_match": 85,
  "education_match": 80,
  "overall_fit": 85,
  "matched_skills": ["Python", "FastAPI", "Docker"],
  "missing_skills": ["Kubernetes"],
  "analysis": "Strong technical match with relevant experience."
}"""

MOCK_DECIDE_RESPONSE = """{
  "score": 85,
  "summary": "Strong candidate with 5 years Python experience and relevant skills.",
  "strengths": ["Deep Python expertise", "FastAPI production experience", "Docker skills"],
  "weaknesses": ["No Kubernetes experience"],
  "recommendation": "Hire"
}"""


def _mock_gemini_call(prompt: str) -> str:
    """Route mock responses based on prompt content."""
    if "data extraction agent" in prompt.lower():
        return MOCK_EXTRACT_RESPONSE
    elif "job-matching analysis agent" in prompt.lower():
        return MOCK_MATCH_RESPONSE
    elif "hiring decision agent" in prompt.lower():
        return MOCK_DECIDE_RESPONSE
    return "{}"


@patch("app.services.screening_pipeline._call_gemini", side_effect=_mock_gemini_call)
def test_extract_resume_data(mock_call):
    """Extract agent returns structured resume data."""
    result = extract_resume_data("Jane Doe, Python dev, 5 years experience")
    assert result["name"] == "Jane Doe"
    assert "Python" in result["skills"]
    assert result["experience_years"] == 5
    assert result["education"] == "BS Computer Science, MIT"
    mock_call.assert_called_once()


@patch("app.services.screening_pipeline._call_gemini", side_effect=_mock_gemini_call)
def test_match_against_job(mock_call):
    """Match agent scores the candidate against job requirements."""
    extracted = {
        "skills": ["Python", "FastAPI"],
        "experience_years": 5,
        "education": "BS CS",
        "certifications": [],
        "recent_role": "Dev at Co",
        "summary": "Python dev.",
    }
    result = match_against_job(extracted, "Python Dev", "Build APIs", "Python, FastAPI")
    assert result["skill_match"] == 90
    assert result["overall_fit"] == 85
    assert "Python" in result["matched_skills"]
    mock_call.assert_called_once()


@patch("app.services.screening_pipeline._call_gemini", side_effect=_mock_gemini_call)
def test_make_decision(mock_call):
    """Decide agent synthesises a final recommendation."""
    extracted = {"name": "Jane", "experience_years": 5, "recent_role": "Dev", "education": "BS"}
    match_result = {"skill_match": 90, "experience_match": 85, "education_match": 80,
                    "overall_fit": 85, "matched_skills": ["Python"], "missing_skills": [], "analysis": "Good"}
    result = make_decision(extracted, match_result)
    assert result["score"] == 85
    assert result["recommendation"] == "Hire"
    assert len(result["strengths"]) > 0
    mock_call.assert_called_once()


@patch("app.services.screening_pipeline._call_gemini", side_effect=_mock_gemini_call)
def test_full_pipeline(mock_call):
    """Full pipeline runs all 3 steps and returns decision + trace."""
    result = run_screening_pipeline(
        resume_text="Jane Doe, Python dev, 5 years",
        job_title="Python Developer",
        job_description="Build APIs.",
        job_requirements="Python, FastAPI, Docker.",
    )

    assert result["score"] == 85
    assert result["recommendation"] == "Hire"
    assert "pipeline_trace" in result
    assert "extracted_profile" in result["pipeline_trace"]
    assert "match_analysis" in result["pipeline_trace"]
    assert result["pipeline_trace"]["extracted_profile"]["name"] == "Jane Doe"
    assert result["pipeline_trace"]["match_analysis"]["overall_fit"] == 85
    assert mock_call.call_count == 3  # extract + match + decide


@patch("app.services.screening_pipeline._call_gemini", return_value="invalid json{{{")
def test_extract_handles_parse_error(mock_call):
    """Extract agent returns fallback dict on JSON parse failure."""
    result = extract_resume_data("bad resume")
    assert result["skills"] == []
    assert result["experience_years"] == 0
    assert "error" in result


@patch("app.services.screening_pipeline._call_gemini", return_value="invalid json{{{")
def test_match_handles_parse_error(mock_call):
    """Match agent returns zeroed scores on failure."""
    result = match_against_job({}, "Title", "Desc", "Reqs")
    assert result["overall_fit"] == 0
    assert "error" in result


@patch("app.services.screening_pipeline._call_gemini", return_value="invalid json{{{")
def test_decide_handles_parse_error(mock_call):
    """Decide agent returns safe defaults on failure."""
    result = make_decision({}, {})
    assert result["score"] == 0
    assert result["recommendation"] == "Error"
    assert "error" in result


@patch("app.services.screening_pipeline._call_gemini", side_effect=_mock_gemini_call)
def test_pipeline_score_clamping(mock_call):
    """Scores are clamped to 0-100 range."""
    result = run_screening_pipeline("resume", "title", "desc", "reqs")
    assert 0 <= result["score"] <= 100


@patch("app.services.screening_pipeline._call_gemini", return_value='```json\n{"name":"Test","email":null,"skills":["Go"],"experience_years":2,"education":"BS","certifications":[],"recent_role":"Dev","summary":"Go dev"}\n```')
def test_extract_strips_markdown_fences(mock_call):
    """Extract agent handles markdown-fenced JSON responses."""
    result = extract_resume_data("test resume")
    assert result["name"] == "Test"
    assert "Go" in result["skills"]
