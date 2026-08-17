"""Tests for cohort-scoped visibility and dashboard endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"vis-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from app.main import app

    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager

    from app.core.database import engine

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Vis"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"V-{uuid.uuid4().hex[:6]}"}, headers=h)
    return r.json()["data"]["id"]


async def _setup_cohort_with_project(c, h_instructor, oid, h_student, student_id):
    """Create a cohort, enroll the student, create + publish + assign a project."""
    cid = (
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts", json={"name": "Test Cohort"}, headers=h_instructor
        )
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": student_id, "role": "learner"},
        headers=h_instructor,
    )
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Cohort Project",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h_instructor,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h_instructor)
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects",
        json={"project_id": pid},
        headers=h_instructor,
    )
    return cid, pid


# ── Visibility ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_student_sees_org_wide_and_cohort_projects(c):
    """A student sees org-wide projects (no cohort assignment) PLUS projects
    assigned to their cohort — but NOT another cohort's projects."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )

    # Org-wide project (no cohort assignment)
    ow_pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Org Wide",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=hi,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{ow_pid}/publish", headers=hi)

    # Cohort A project (student is in cohort A)
    cid_a, pid_a = await _setup_cohort_with_project(c, hi, oid, hs, us["id"])

    # Cohort B project (student is NOT in cohort B)
    _, u3 = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u3["id"], "role": "student"}, headers=hi
    )
    cid_b = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Cohort B"}, headers=hi)
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid_b}/members", json={"user_id": u3["id"]}, headers=hi
    )
    pid_b = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Cohort B Only",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=hi,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid_b}/publish", headers=hi)
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid_b}/projects", json={"project_id": pid_b}, headers=hi
    )

    # Student lists projects
    r = await c.get(f"/api/v1/orgs/{oid}/projects", headers=hs)
    titles = {p["title"] for p in r.json()["data"]}
    assert "Org Wide" in titles  # org-wide visible
    assert "Cohort Project" in titles  # own cohort visible
    assert "Cohort B Only" not in titles  # other cohort hidden


@pytest.mark.asyncio
async def test_instructor_sees_all_projects(c):
    """Instructors see all projects regardless of cohort assignment."""
    hi, _ = await _auth(c)
    oid = await _org(c, hi)
    hs, us = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )
    await _setup_cohort_with_project(c, hi, oid, hs, us["id"])
    r = await c.get(f"/api/v1/orgs/{oid}/projects", headers=hi)
    assert r.json()["meta"]["total"] >= 1  # instructor sees everything


@pytest.mark.asyncio
async def test_cohort_filter_on_projects(c):
    """The cohort_id query param filters projects to a specific cohort."""
    hi, _ = await _auth(c)
    oid = await _org(c, hi)
    hs, us = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )
    cid, pid = await _setup_cohort_with_project(c, hi, oid, hs, us["id"])
    r = await c.get(f"/api/v1/orgs/{oid}/projects?cohort_id={cid}", headers=hi)
    assert r.json()["meta"]["total"] == 1
    assert r.json()["data"][0]["title"] == "Cohort Project"


@pytest.mark.asyncio
async def test_backward_compat_no_cohort(c):
    """When no cohorts exist, org-wide projects behave exactly as before."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Legacy Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=hi,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=hi)
    r = await c.get(f"/api/v1/orgs/{oid}/projects", headers=hs)
    assert any(p["title"] == "Legacy Proj" for p in r.json()["data"])


# ── Dashboard ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cohort_progress_dashboard(c):
    """Instructor can see aggregate progress metrics for a cohort."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )
    cid, pid = await _setup_cohort_with_project(c, hi, oid, hs, us["id"])

    # Student submits
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=hs)

    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress", headers=hi)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total_learners"] == 1
    assert len(data["projects"]) == 1
    assert data["projects"][0]["submitted"] == 1


@pytest.mark.asyncio
async def test_learner_drill_down(c):
    """Instructor can drill into a specific learner's progress within a cohort."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )
    cid, pid = await _setup_cohort_with_project(c, hi, oid, hs, us["id"])

    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress/{us['id']}", headers=hi)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["user_name"] == "Vis"
    assert len(data["projects"]) == 1
    assert data["projects"][0]["submission_status"] == "not_started"


@pytest.mark.asyncio
async def test_learner_dashboard(c):
    """Learner can view their own cohort dashboard."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )
    cid, pid = await _setup_cohort_with_project(c, hi, oid, hs, us["id"])

    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/my-dashboard", headers=hs)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["cohort"]["name"] == "Test Cohort"
    assert len(data["assigned_projects"]) == 1


@pytest.mark.asyncio
async def test_student_cannot_see_progress_dashboard(c):
    """Students cannot access the instructor progress dashboard."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )
    cid, _ = await _setup_cohort_with_project(c, hi, oid, hs, us["id"])
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress", headers=hs)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_empty_cohort_progress(c):
    """Progress endpoint returns zero counts for an empty cohort (no crash)."""
    hi, _ = await _auth(c)
    oid = await _org(c, hi)
    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Empty"}, headers=hi)).json()[
        "data"
    ]["id"]
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress", headers=hi)
    assert r.status_code == 200
    assert r.json()["data"]["total_learners"] == 0
    assert r.json()["data"]["projects"] == []
