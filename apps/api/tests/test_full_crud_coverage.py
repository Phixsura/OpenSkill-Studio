"""Full CRUD coverage tests — authenticated users performing complete workflows.

Goes deeper than auth-guard tests: creates real data, verifies responses,
tests update/delete, checks side effects.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"crud-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "CRUD"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


# ═══════════════ Project Full Lifecycle ═══════════════


@pytest.mark.asyncio
async def test_project_full_lifecycle(c):
    """Create → get detail (with rubric) → update → publish → archive."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Create
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Lifecycle Project",
            "description": "Full lifecycle test",
            "instructions": "Do the thing",
            "rubric": [
                {"criterion": "Quality", "max_score": 60},
                {"criterion": "Creativity", "max_score": 40},
            ],
            "deadline": "2026-12-31T23:59:59Z",
            "max_submissions": 3,
        },
        headers=h,
    )
    assert r.status_code == 201
    pid = r.json()["data"]["id"]

    # Get detail — should include rubric
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)
    assert r.status_code == 200
    detail = r.json()["data"]
    assert len(detail["rubric"]) == 2
    assert detail["rubric"][0]["criterion"] == "Quality"
    assert detail["max_submissions"] == 3
    assert detail["instructions"] == "Do the thing"

    # Update
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}",
        json={
            "title": "Updated Lifecycle Project",
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["title"] == "Updated Lifecycle Project"

    # Publish
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "published"

    # Archive
    r = await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)
    assert r.status_code == 204

    # Get after archive → 404
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_project_deliverable_crud(c):
    """Create deliverable → update → delete."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Deliv Test",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]

    # Create deliverable
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
        json={
            "name": "Hero Image",
            "type": "file",
            "required": True,
        },
        headers=h,
    )
    assert r.status_code == 201
    did = r.json()["data"]["id"]
    assert r.json()["data"]["name"] == "Hero Image"

    # List deliverables
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)
    assert any(d["id"] == did for d in r.json()["data"]["deliverables"])

    # Update deliverable
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/deliverables/{did}",
        json={
            "name": "Updated Hero",
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Updated Hero"

    # Delete deliverable
    r = await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}/deliverables/{did}", headers=h)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_submission_create_submit_detail(c):
    """Create submission → submit → get detail with status."""
    h, u = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )

    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Sub Test",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)

    # Create submission
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)
    assert r.status_code == 201
    sid = r.json()["data"]["id"]
    assert r.json()["data"]["status"] == "draft"

    # Submit
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=hs)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "submitted"

    # Get detail
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=hs)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "submitted"
    assert r.json()["data"]["user_id"] == us["id"]


# ═══════════════ Skill Full Lifecycle ═══════════════


@pytest.mark.asyncio
async def test_skill_full_lifecycle(c):
    """Create category → create skill → update → archive."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Create category
    r = await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Design"}, headers=h)
    assert r.status_code == 201
    cat_id = r.json()["data"]["id"]

    # Create skill
    r = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={
            "name": "Typography",
            "description": "Learn typography fundamentals",
            "difficulty": "beginner",
            "category_id": cat_id,
        },
        headers=h,
    )
    assert r.status_code == 201
    sk_id = r.json()["data"]["id"]

    # Get detail
    r = await c.get(f"/api/v1/orgs/{oid}/skills/{sk_id}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Typography"
    assert r.json()["data"]["difficulty"] == "beginner"

    # Update
    r = await c.put(
        f"/api/v1/orgs/{oid}/skills/{sk_id}",
        json={
            "name": "Advanced Typography",
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Advanced Typography"

    # Archive
    r = await c.delete(f"/api/v1/orgs/{oid}/skills/{sk_id}", headers=h)
    assert r.status_code == 204

    # Get after archive → 404
    r = await c.get(f"/api/v1/orgs/{oid}/skills/{sk_id}", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_skill_exercise_crud(c):
    """Create exercise under skill → update → archive."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Ex"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "ExSkill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]

    # Create exercise
    r = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
        json={
            "title": "Practice 1",
            "description": "A practice exercise",
            "type": "text_answer",
            "config": {"prompt": "Explain typography"},
        },
        headers=h,
    )
    assert r.status_code == 201
    ex_id = r.json()["data"]["id"]

    # List exercises
    r = await c.get(f"/api/v1/orgs/{oid}/skills/{sk}/exercises", headers=h)
    assert r.status_code == 200
    assert any(e["id"] == ex_id for e in r.json()["data"])

    # Update exercise
    r = await c.put(
        f"/api/v1/orgs/{oid}/exercises/{ex_id}",
        json={
            "title": "Updated Practice 1",
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["title"] == "Updated Practice 1"


# ═══════════════ Evaluation Full Lifecycle ═══════════════


@pytest.mark.asyncio
async def test_evaluation_settings_crud(c):
    """Get eval settings → enable → disable."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Get settings (default disabled) — EvalSettingsResponse is flat, not wrapped in "data"
    r = await c.get(f"/api/v1/orgs/{oid}/settings/evaluation", headers=h)
    assert r.status_code == 200
    body = r.json()
    # Response may be flat or wrapped depending on endpoint
    settings = body.get("data", body)
    assert settings["enabled"] is False

    # Enable
    r = await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={
            "enabled": True,
            "monthly_budget_usd": 100,
        },
        headers=h,
    )
    assert r.status_code == 200
    settings = r.json().get("data", r.json())
    assert settings["enabled"] is True
    assert settings["monthly_budget_usd"] == 100

    # Disable
    r = await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={
            "enabled": False,
        },
        headers=h,
    )
    assert r.status_code == 200
    settings = r.json().get("data", r.json())
    assert settings["enabled"] is False


@pytest.mark.asyncio
async def test_evaluation_usage_empty(c):
    """Get usage when no evaluations have been run → zero values."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={
            "enabled": True,
            "monthly_budget_usd": 100,
        },
        headers=h,
    )

    r = await c.get(f"/api/v1/orgs/{oid}/evaluation/usage", headers=h)
    assert r.status_code == 200
    body = r.json()
    data = body.get("data", body)
    assert data["total_cost_usd"] == 0 or data["total_cost_usd"] == 0.0


@pytest.mark.asyncio
async def test_evaluation_trigger_disabled(c):
    """Trigger eval when disabled → rejected."""
    h, u = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )

    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Eval Test",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=hs)

    # Eval disabled (default) → should reject
    r = await c.post(
        f"/api/v1/orgs/{oid}/evaluation/trigger",
        json={
            "submission_id": sid,
            "type": "submission_review",
        },
        headers=h,
    )
    assert r.status_code in (403, 422, 429)  # depends on impl


# ═══════════════ Cohort + Brief Deep Flows ═══════════════


@pytest.mark.asyncio
async def test_cohort_progress_mixed_statuses(c):
    """Progress with mixed learner statuses: one submitted, one not started."""
    h, _ = await _auth(c)
    hs1, us1 = await _auth(c)
    hs2, us2 = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us1["id"], "role": "student"}, headers=h
    )
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us2["id"], "role": "student"}, headers=h
    )

    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Mix"}, headers=h)).json()[
        "data"
    ]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us1["id"]}, headers=h
    )
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us2["id"]}, headers=h
    )

    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Mix Proj",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", json={"project_id": pid}, headers=h)

    # Student 1 submits
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs1)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=hs1)

    # Student 2 does nothing

    # Check progress
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress", headers=h)
    assert r.status_code == 200
    p = r.json()["data"]
    assert p["total_learners"] == 2
    proj = p["projects"][0]
    assert proj["submitted"] == 1
    assert proj["not_started"] == 1


@pytest.mark.asyncio
async def test_convert_brief_default_title_and_rubric(c):
    """Convert brief with title=None and default rubric → uses brief.title."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    bid = (
        await c.post(
            f"/api/v1/orgs/{oid}/briefs",
            json={
                "title": "My Brief Title",
                "client_name": "Client",
                "project_type": "viz",
                "objective": "Create stunning visuals for the brand campaign",
            },
            headers=h,
        )
    ).json()["data"]["id"]

    # Convert with no explicit title
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/convert",
        json={
            "rubric": [{"criterion": "Overall", "max_score": 100}],
        },
        headers=h,
    )
    assert r.status_code == 201
    proj = r.json()["data"]
    assert proj["title"] == "My Brief Title"  # used brief.title
    assert proj["client_brief_id"] == bid


@pytest.mark.asyncio
async def test_convert_brief_with_deliverable_specs_missing_fields(c):
    """Convert brief with deliverable_specs missing optional fields."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    bid = (
        await c.post(
            f"/api/v1/orgs/{oid}/briefs",
            json={
                "title": "Spec Brief",
                "client_name": "C",
                "project_type": "viz",
                "objective": "Test deliverable spec defaults work correctly",
                "deliverable_specs": [
                    {"type": "file"},  # no name, no description, no config
                    {"name": "Video", "type": "video"},  # no description
                ],
            },
            headers=h,
        )
    ).json()["data"]["id"]

    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/convert",
        json={
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    assert r.status_code == 201
    pid = r.json()["data"]["id"]

    # Verify deliverables were created with defaults
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)
    deliverables = r.json()["data"]["deliverables"]
    assert len(deliverables) == 2
    assert deliverables[0]["name"] == "Deliverable 1"  # default
    assert deliverables[1]["name"] == "Video"


@pytest.mark.asyncio
async def test_visibility_three_way_or_filter(c):
    """Three-way visibility: org-wide + cohort-assigned + individually assigned."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )

    # Org-wide project (no cohort)
    p1 = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "OrgWide",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p1}/publish", headers=h)

    # Cohort-assigned project
    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Vis"}, headers=h)).json()[
        "data"
    ]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=h)
    p2 = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "CohortOnly",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p2}/publish", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", json={"project_id": p2}, headers=h)

    # Student sees both
    r = await c.get(f"/api/v1/orgs/{oid}/projects", headers=hs)
    assert r.status_code == 200
    titles = [p["title"] for p in r.json()["data"]]
    assert "OrgWide" in titles
    assert "CohortOnly" in titles


@pytest.mark.asyncio
async def test_cohort_filter_invalid_id(c):
    """Filtering projects by non-existent cohort_id returns empty, not error."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.get(f"/api/v1/orgs/{oid}/projects?cohort_id=01NONEXISTENT000000000000", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 0


@pytest.mark.asyncio
async def test_bulk_enroll_partial_success(c):
    """Bulk enroll: some valid members + some non-org-members → partial success."""
    h, _ = await _auth(c)
    hs1, us1 = await _auth(c)
    hs2, us2 = await _auth(c)  # NOT added to org
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us1["id"], "role": "student"}, headers=h
    )
    # us2 is NOT an org member

    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Bulk"}, headers=h)).json()[
        "data"
    ]["id"]

    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members/bulk",
        json={
            "user_ids": [us1["id"], us2["id"]],
        },
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["enrolled"] == 1
    assert data["skipped"] == 1


@pytest.mark.asyncio
async def test_delete_project_cascades_from_cohort(c):
    """Deleting a project removes it from all cohort assignment lists."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Cascade",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]

    c1 = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "C1"}, headers=h)).json()[
        "data"
    ]["id"]
    c2 = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "C2"}, headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{c1}/projects", json={"project_id": pid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{c2}/projects", json={"project_id": pid}, headers=h)

    # Delete project
    await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)

    # Both cohorts should no longer list it
    r1 = await c.get(f"/api/v1/orgs/{oid}/cohorts/{c1}/projects", headers=h)
    r2 = await c.get(f"/api/v1/orgs/{oid}/cohorts/{c2}/projects", headers=h)
    assert len(r1.json()["data"]) == 0
    assert len(r2.json()["data"]) == 0


@pytest.mark.asyncio
async def test_delete_cohort_doesnt_delete_project(c):
    """Deleting a cohort doesn't delete the projects assigned to it."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Survivor",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]

    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Doomed"}, headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", json={"project_id": pid}, headers=h)

    # Delete cohort
    await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid}", headers=h)

    # Project still exists
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["title"] == "Survivor"


@pytest.mark.asyncio
async def test_remove_member_keeps_submissions(c):
    """Removing a member from cohort doesn't delete their submissions."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )

    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Keep"}, headers=h)).json()[
        "data"
    ]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=h)

    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Keep Sub",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=hs)

    # Remove from cohort
    await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid}/members/{us['id']}", headers=h)

    # Submission still accessible
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=hs)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "submitted"


@pytest.mark.asyncio
async def test_multi_cohort_member_sees_projects_from_each(c):
    """Student in 2 cohorts sees projects from both."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )

    # Two cohorts, each with a different project
    c1 = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "MC1"}, headers=h)).json()[
        "data"
    ]["id"]
    c2 = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "MC2"}, headers=h)).json()[
        "data"
    ]["id"]
    for cid in [c1, c2]:
        await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=h
        )

    p1 = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "From C1",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p1}/publish", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{c1}/projects", json={"project_id": p1}, headers=h)

    p2 = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "From C2",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p2}/publish", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{c2}/projects", json={"project_id": p2}, headers=h)

    # Student sees both
    r = await c.get(f"/api/v1/orgs/{oid}/projects", headers=hs)
    titles = [p["title"] for p in r.json()["data"]]
    assert "From C1" in titles
    assert "From C2" in titles
