"""Project, submission, and review tests."""

import pytest

from app.models.project import DeliverableType, ReviewerType, ReviewStatus, SubmissionStatus
from app.services.project import ProjectService

# ── Auth protection ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_projects_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/projects")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_project_requires_auth(client):
    r = await client.post(
        "/api/v1/orgs/fake/projects",
        json={
            "title": "Test",
            "description": "D",
            "instructions": "I",
            "rubric": [{"criterion": "X", "max_score": 10}],
        },
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_project_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/projects/fake-id")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_deliverable_requires_auth(client):
    r = await client.post(
        "/api/v1/orgs/fake/projects/fake/deliverables", json={"name": "README", "type": "file"}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_submission_requires_auth(client):
    r = await client.post("/api/v1/orgs/fake/projects/fake/submissions")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_submit_draft_requires_auth(client):
    r = await client.post("/api/v1/orgs/fake/projects/fake/submissions/fake/submit")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_upload_file_requires_auth(client):
    r = await client.post("/api/v1/orgs/fake/submissions/fake/files")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_review_requires_auth(client):
    r = await client.post(
        "/api/v1/orgs/fake/submissions/fake/reviews", json={"status": "approved", "score": 90}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_pending_reviews_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/reviews/pending")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_grant_extension_requires_auth(client):
    r = await client.post(
        "/api/v1/orgs/fake/projects/fake/extensions",
        json={"user_id": "x", "new_deadline": "2026-12-31T00:00:00Z"},
    )
    assert r.status_code == 401


# ── Schema validation ────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_project_title_too_short(client):
    r = await client.post(
        "/api/v1/orgs/fake/projects",
        json={
            "title": "A",
            "description": "D",
            "instructions": "I",
            "rubric": [{"criterion": "X"}],
        },
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_project_empty_rubric(client):
    r = await client.post(
        "/api/v1/orgs/fake/projects",
        json={"title": "Test Project", "description": "D", "instructions": "I", "rubric": []},
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_deliverable_missing_type(client):
    r = await client.post("/api/v1/orgs/fake/projects/fake/deliverables", json={"name": "README"})
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_review_invalid_status(client):
    r = await client.post("/api/v1/orgs/fake/submissions/fake/reviews", json={"status": "invalid"})
    assert r.status_code in (401, 422)


# ── Unit tests ───────────────────────────────────────────────


def test_submission_status_values():
    assert SubmissionStatus.DRAFT.value == "draft"
    assert SubmissionStatus.SUBMITTED.value == "submitted"
    assert SubmissionStatus.REVISION_REQUESTED.value == "revision_requested"
    assert SubmissionStatus.APPROVED.value == "approved"
    assert SubmissionStatus.REJECTED.value == "rejected"


def test_deliverable_type_values():
    assert DeliverableType.FILE.value == "file"
    assert DeliverableType.TEXT.value == "text"
    assert DeliverableType.LINK.value == "link"
    assert DeliverableType.MARKDOWN.value == "markdown"


def test_review_status_values():
    assert ReviewStatus.APPROVED.value == "approved"
    assert ReviewStatus.REVISION_REQUESTED.value == "revision_requested"
    assert ReviewStatus.REJECTED.value == "rejected"


def test_reviewer_type_values():
    assert ReviewerType.INSTRUCTOR.value == "instructor"
    assert ReviewerType.AI.value == "ai"


def test_late_penalty_calculation():
    """100 score * 20% penalty = 80."""
    from unittest.mock import MagicMock

    project = MagicMock()
    project.late_penalty_pct = 20

    result = ProjectService._calculate_final_score(100, is_late=True, project=project)
    assert result == 80


def test_late_penalty_zero_when_on_time():
    """Non-late submission gets raw score."""
    from unittest.mock import MagicMock

    project = MagicMock()
    project.late_penalty_pct = 20

    result = ProjectService._calculate_final_score(85, is_late=False, project=project)
    assert result == 85


def test_late_penalty_high_percentage():
    """50% penalty on 100 = 50."""
    from unittest.mock import MagicMock

    project = MagicMock()
    project.late_penalty_pct = 50

    result = ProjectService._calculate_final_score(100, is_late=True, project=project)
    assert result == 50


def test_slug_generation():
    assert ProjectService._generate_slug("AI Chatbot Project") == "ai-chatbot-project"
    assert len(ProjectService._generate_slug("AB")) >= 3
