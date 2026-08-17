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


# ── Visibility edge cases ────────────────────────────────


@pytest.mark.asyncio
async def test_skill_visibility_with_cohort_filter(c):
    """cohort_id query param filters skills to a specific cohort."""
    hi, _ = await _auth(c)
    oid = await _org(c, hi)
    hs, us = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )
    cat = (
        await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Vis Cat"}, headers=hi)
    ).json()["data"]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Cohort Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=hi,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/skills/{sk}/publish", headers=hi)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Skill Vis"}, headers=hi)
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/skills", json={"skill_id": sk}, headers=hi)
    r = await c.get(f"/api/v1/orgs/{oid}/skills?cohort_id={cid}", headers=hi)
    assert r.json()["meta"]["total"] == 1
    assert r.json()["data"][0]["name"] == "Cohort Skill"


@pytest.mark.asyncio
async def test_student_in_two_cohorts_sees_both(c):
    """A student in cohort A and cohort B sees both cohorts' projects."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )

    projects = []
    for name in ("Cohort A", "Cohort B"):
        cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": name}, headers=hi)).json()[
            "data"
        ]["id"]
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=hi
        )
        pid = (
            await c.post(
                f"/api/v1/orgs/{oid}/projects",
                json={
                    "title": f"{name} Project",
                    "description": "d",
                    "instructions": "i",
                    "rubric": [{"criterion": "Q", "max_score": 100}],
                },
                headers=hi,
            )
        ).json()["data"]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=hi)
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", json={"project_id": pid}, headers=hi
        )
        projects.append(f"{name} Project")

    r = await c.get(f"/api/v1/orgs/{oid}/projects", headers=hs)
    titles = {p["title"] for p in r.json()["data"]}
    for title in projects:
        assert title in titles


@pytest.mark.asyncio
async def test_max_submissions_override_enforced(c):
    """Cohort max_submissions_override takes precedence over project default."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )

    # Project allows unlimited (0)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Max Test",
                "description": "d",
                "instructions": "i",
                "max_submissions": 0,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=hi,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=hi)

    # Cohort restricts to 1
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Max Override"}, headers=hi)
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=hi
    )
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects",
        json={"project_id": pid, "max_submissions_override": 1},
        headers=hi,
    )

    # First submission OK
    assert (
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)
    ).status_code == 201
    # Second blocked by override
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)
    assert r.status_code == 422
    assert "Maximum" in r.json()["error"]["message"]


@pytest.mark.asyncio
async def test_progress_with_overdue_detection(c):
    """Dashboard correctly detects overdue submissions."""
    from datetime import UTC, datetime, timedelta

    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )

    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Overdue Proj",
                "description": "d",
                "instructions": "i",
                "deadline": past,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=hi,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=hi)

    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Overdue Cohort"}, headers=hi)
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=hi
    )
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", json={"project_id": pid}, headers=hi)

    progress = (await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress", headers=hi)).json()[
        "data"
    ]
    assert progress["overdue_submissions"] >= 1
    assert progress["projects"][0]["overdue"] >= 1


@pytest.mark.asyncio
async def test_drill_down_mixed_statuses(c):
    """Learner drill-down shows correct status for each project."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )

    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Mixed Status"}, headers=hi)
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=hi
    )

    # Two projects: one submitted, one not started
    for title in ("Submitted Proj", "NotStarted Proj"):
        pid = (
            await c.post(
                f"/api/v1/orgs/{oid}/projects",
                json={
                    "title": title,
                    "description": "d",
                    "instructions": "i",
                    "rubric": [{"criterion": "Q", "max_score": 100}],
                },
                headers=hi,
            )
        ).json()["data"]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=hi)
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", json={"project_id": pid}, headers=hi
        )
        if title == "Submitted Proj":
            sid = (
                await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)
            ).json()["data"]["id"]
            await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=hs)

    drill = (
        await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress/{us['id']}", headers=hi)
    ).json()["data"]
    statuses = {p["title"]: p["submission_status"] for p in drill["projects"]}
    assert statuses["Submitted Proj"] == "submitted"
    assert statuses["NotStarted Proj"] == "not_started"


@pytest.mark.asyncio
async def test_inactive_learners_count(c):
    """Dashboard reports inactive learners (no activity in 7+ days)."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )

    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Inactive Test"}, headers=hi)
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=hi
    )

    # No submissions = inactive
    progress = (await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress", headers=hi)).json()[
        "data"
    ]
    assert progress["inactive_learners_7d"] == 1
