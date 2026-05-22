"""API endpoint integration tests.

These tests verify routing, validation, and database operations. They do NOT
call the Gemini API — screening tests are in test_screening.py.
"""


def test_root_returns_message(client):
    """Root endpoint returns a helpful message when SPA is not built."""
    resp = client.get("/")
    # Might return JSON message or serve SPA — both are valid
    assert resp.status_code == 200


def test_list_jobs(client):
    """GET /api/jobs returns a list (includes seeded demo jobs)."""
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_job(client):
    """POST /api/jobs creates a job and returns it with an ID."""
    payload = {
        "title": "ML Engineer",
        "company": "AI Corp",
        "location": "Remote",
        "job_type": "Full-time",
        "description": "Build ML models.",
        "requirements": "Python, PyTorch.",
    }
    resp = client.post("/api/jobs", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "ML Engineer"
    assert data["id"]  # UUID was generated
    assert data["applications_count"] == 0


def test_get_job(client):
    """GET /api/jobs/{id} returns the correct job."""
    create_resp = client.post("/api/jobs", json={
        "title": "DevOps",
        "company": "Cloud Inc",
        "location": "NYC",
        "job_type": "Contract",
        "description": "Manage infra.",
        "requirements": "AWS, Terraform.",
    })
    job_id = create_resp.json()["id"]

    resp = client.get(f"/api/jobs/{job_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "DevOps"


def test_get_job_not_found(client):
    """GET /api/jobs/{id} returns 404 for non-existent jobs."""
    resp = client.get("/api/jobs/nonexistent-id")
    assert resp.status_code == 404


def test_delete_job(client):
    """DELETE /api/jobs/{id} removes the job."""
    create_resp = client.post("/api/jobs", json={
        "title": "Temp Job",
        "company": "Temp Co",
        "location": "Anywhere",
        "job_type": "Part-time",
        "description": "Temporary.",
        "requirements": "None.",
    })
    job_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/jobs/{job_id}")
    assert del_resp.status_code == 200

    get_resp = client.get(f"/api/jobs/{job_id}")
    assert get_resp.status_code == 404


def test_list_applications_empty(client):
    """GET /api/jobs/{id}/applications returns empty list for a new job."""
    # Create a job via API so it exists in the API's session
    job_resp = client.post("/api/jobs", json={
        "title": "Test Job",
        "company": "Test Co",
        "location": "Remote",
        "job_type": "Full-time",
        "description": "Test.",
        "requirements": "None.",
    })
    job_id = job_resp.json()["id"]
    resp = client.get(f"/api/jobs/{job_id}/applications")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_applications_not_found(client):
    """GET /api/jobs/{id}/applications returns 404 for non-existent job."""
    resp = client.get("/api/jobs/fake-id/applications")
    assert resp.status_code == 404


def test_stats_endpoint(client):
    """GET /api/stats returns aggregate statistics."""
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_jobs" in data
    assert "total_applications" in data
    assert "screened_applications" in data
    assert "average_score" in data


def test_screen_no_applications(client):
    """POST /api/jobs/{id}/screen returns 400 when there's nothing to screen."""
    job_resp = client.post("/api/jobs", json={
        "title": "Screen Test",
        "company": "SC",
        "location": "Remote",
        "job_type": "Full-time",
        "description": "Test.",
        "requirements": "None.",
    })
    job_id = job_resp.json()["id"]
    resp = client.post(f"/api/jobs/{job_id}/screen")
    assert resp.status_code == 400
    assert "unscreened" in resp.json()["detail"].lower()


def test_screen_job_not_found(client):
    """POST /api/jobs/{id}/screen returns 404 for non-existent job."""
    resp = client.post("/api/jobs/fake-id/screen")
    assert resp.status_code == 404


def test_screen_single_not_found(client):
    """POST /api/applications/{id}/screen returns 404 for non-existent app."""
    resp = client.post("/api/applications/fake-id/screen")
    assert resp.status_code == 404


def test_draft_email_not_screened(client):
    """POST /draft-email returns 400 if application hasn't been screened.

    We create a job and submit an application via the API, then try to
    draft an email without screening first.
    """
    # Create job
    job_resp = client.post("/api/jobs", json={
        "title": "Email Test",
        "company": "EM",
        "location": "Remote",
        "job_type": "Full-time",
        "description": "Test.",
        "requirements": "None.",
    })
    job_id = job_resp.json()["id"]

    # Submit application with a dummy PDF
    import io
    dummy_pdf = io.BytesIO(b"%PDF-1.4 dummy content")
    apply_resp = client.post(
        f"/api/jobs/{job_id}/apply",
        data={"name": "Test User", "email": "test@test.com"},
        files={"resume": ("test.pdf", dummy_pdf, "application/pdf")},
    )
    app_id = apply_resp.json()["application_id"]

    # Try drafting email without screening
    resp = client.post(
        f"/api/applications/{app_id}/draft-email",
        params={"kind": "interview"},
    )
    assert resp.status_code == 400
    assert "screen" in resp.json()["detail"].lower()


def test_draft_email_not_found(client):
    """POST /draft-email returns 404 for non-existent application."""
    resp = client.post(
        "/api/applications/fake-id/draft-email",
        params={"kind": "interview"},
    )
    assert resp.status_code == 404
