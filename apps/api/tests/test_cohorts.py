"""Integration tests for cohort management."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"coh-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Coh"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


# ── Cohort CRUD ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_cohort(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={"name": "AI Visual — Fall 2026", "description": "First cohort"},
        headers=h,
    )
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["name"] == "AI Visual — Fall 2026"
    assert d["status"] == "draft"
    assert d["member_count"] == 0


@pytest.mark.asyncio
async def test_list_cohorts(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Cohort Alpha"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Cohort Beta"}, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 2
    assert r.json()["meta"]["total"] == 2


@pytest.mark.asyncio
async def test_update_cohort_status(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Status Test"}, headers=h)
    ).json()["data"]["id"]
    r = await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_delete_draft_only(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Delete Test"}, headers=h)
    ).json()["data"]["id"]
    assert (await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid}", headers=h)).status_code == 204
    # non-draft: reject
    cid2 = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Active Test"}, headers=h)
    ).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid2}", json={"status": "active"}, headers=h)
    assert (await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid2}", headers=h)).status_code == 422


@pytest.mark.asyncio
async def test_cross_org_cohort_hidden(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    o1 = await _org(c, h1)
    await _org(c, h2)
    cid = (
        await c.post(f"/api/v1/orgs/{o1}/cohorts", json={"name": "Org1 Cohort"}, headers=h1)
    ).json()["data"]["id"]
    # user2 is NOT a member of org1
    r = await c.get(f"/api/v1/orgs/{o1}/cohorts/{cid}", headers=h2)
    assert r.status_code == 403  # not an org member


@pytest.mark.asyncio
async def test_cohort_name_validation(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "X"}, headers=h)
    assert r.status_code == 422
    r = await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "X" * 300}, headers=h)
    assert r.status_code == 422


# ── Members ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_add_and_remove_member(c):
    h, _ = await _auth(c)
    h2, u2 = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Member Test"}, headers=h)
    ).json()["data"]["id"]
    # add
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u2["id"], "role": "learner"},
        headers=h,
    )
    assert r.status_code == 201
    # duplicate
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u2["id"]},
        headers=h,
    )
    assert r.status_code == 409
    # remove
    r = await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid}/members/{u2['id']}", headers=h)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_non_org_member_rejected(c):
    h, _ = await _auth(c)
    _, u2 = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Non-Org Test"}, headers=h)
    ).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u2["id"]},
        headers=h,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_max_learners_enforced(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts", json={"name": "Max Test", "max_learners": 1}, headers=h
        )
    ).json()["data"]["id"]
    h2, u2 = await _auth(c)
    h3, u3 = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u3["id"], "role": "student"}, headers=h
    )
    assert (
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": u2["id"]}, headers=h
        )
    ).status_code == 201
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": u3["id"]}, headers=h
    )
    assert r.status_code == 422  # full


@pytest.mark.asyncio
async def test_bulk_enroll(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Bulk Test"}, headers=h)
    ).json()["data"]["id"]
    users = []
    for _ in range(3):
        _, u = await _auth(c)
        await c.post(
            f"/api/v1/orgs/{oid}/members", json={"user_id": u["id"], "role": "student"}, headers=h
        )
        users.append(u["id"])
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members/bulk",
        json={"user_ids": users},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["enrolled"] == 3


@pytest.mark.asyncio
async def test_list_members(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "List Members"}, headers=h)
    ).json()["data"]["id"]
    _, u2 = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": u2["id"]}, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/members", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1


# ── Skill Assignment ─────────────────────────────────────


@pytest.mark.asyncio
async def test_assign_and_unassign_skill(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Skill Assign"}, headers=h)
    ).json()["data"]["id"]
    cat = (
        await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "SA Cat"}, headers=h)
    ).json()["data"]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "SA Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    # assign
    r = await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/skills", json={"skill_id": sk}, headers=h)
    assert r.status_code == 201
    # duplicate
    r = await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/skills", json={"skill_id": sk}, headers=h)
    assert r.status_code == 409
    # list
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/skills", headers=h)
    assert len(r.json()["data"]) == 1
    assert r.json()["data"][0]["skill_name"] == "SA Skill"
    # unassign
    r = await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid}/skills/{sk}", headers=h)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_assign_cross_org_skill_rejected(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    o1 = await _org(c, h1)
    o2 = await _org(c, h2)
    cid = (
        await c.post(f"/api/v1/orgs/{o1}/cohorts", json={"name": "Cross Org"}, headers=h1)
    ).json()["data"]["id"]
    cat = (
        await c.post(f"/api/v1/orgs/{o2}/categories", json={"name": "Other Cat"}, headers=h2)
    ).json()["data"]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{o2}/skills",
            json={
                "name": "Other Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h2,
        )
    ).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{o1}/cohorts/{cid}/skills", json={"skill_id": sk}, headers=h1)
    assert r.status_code == 404


# ── Project Assignment ───────────────────────────────────


@pytest.mark.asyncio
async def test_assign_project_with_overrides(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Proj Assign"}, headers=h)
    ).json()["data"]["id"]
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Cohort Project",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects",
        json={
            "project_id": pid,
            "deadline_override": "2030-06-01T00:00:00Z",
            "max_submissions_override": 5,
            "participation_mode": "application",
        },
        headers=h,
    )
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["max_submissions_override"] == 5
    assert d["participation_mode"] == "application"
    # list
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", headers=h)
    assert len(r.json()["data"]) == 1
    assert r.json()["data"][0]["project_title"] == "Cohort Project"


@pytest.mark.asyncio
async def test_assign_cross_org_project_rejected(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    o1 = await _org(c, h1)
    o2 = await _org(c, h2)
    cid = (
        await c.post(f"/api/v1/orgs/{o1}/cohorts", json={"name": "XOrg Proj"}, headers=h1)
    ).json()["data"]["id"]
    pid = (
        await c.post(
            f"/api/v1/orgs/{o2}/projects",
            json={
                "title": "Other Proj",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h2,
        )
    ).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{o1}/cohorts/{cid}/projects", json={"project_id": pid}, headers=h1
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_student_cannot_manage_cohort(c):
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )
    # student tries to create cohort
    r = await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Student Cohort"}, headers=hs)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_cohort_date_ordering(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={
            "name": "Date Order",
            "starts_at": "2030-06-01T00:00:00Z",
            "ends_at": "2029-01-01T00:00:00Z",
        },
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_cohort_status_filter(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Active One"}, headers=h)
    ).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Draft One"}, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts?status=active", headers=h)
    assert r.json()["meta"]["total"] == 1
    assert r.json()["data"][0]["name"] == "Active One"


# ── Edge cases ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_cohort_name_reslugs(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Original Name"}, headers=h)
    ).json()["data"]["id"]
    r = await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"name": "New Name"}, headers=h)
    assert r.status_code == 200
    assert "new-name" in r.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_update_cohort_invalid_status(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Bad Status"}, headers=h)
    ).json()["data"]["id"]
    r = await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "BOGUS"}, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_get_archived_cohort_404(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "To Archive"}, headers=h)
    ).json()["data"]["id"]
    await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid}", headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_add_instructor_to_cohort(c):
    h, _ = await _auth(c)
    h2, u2 = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "instructor"}, headers=h
    )
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Inst Cohort"}, headers=h)
    ).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u2["id"], "role": "instructor"},
        headers=h,
    )
    assert r.status_code == 201
    assert r.json()["data"]["role"] == "instructor"


@pytest.mark.asyncio
async def test_list_members_role_filter(c):
    h, _ = await _auth(c)
    h2, u2 = await _auth(c)
    h3, u3 = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u3["id"], "role": "instructor"}, headers=h
    )
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Filter Test"}, headers=h)
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u2["id"], "role": "learner"},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u3["id"], "role": "instructor"},
        headers=h,
    )
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/members?role=learner", headers=h)
    assert r.json()["meta"]["total"] == 1
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/members?role=instructor", headers=h)
    assert r.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_unassign_nonexistent_skill_404(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Unassign Test"}, headers=h)
    ).json()["data"]["id"]
    r = await c.delete(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/skills/01BOGUSBOGUSBOGUSBOGUSBOGU", headers=h
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_unassign_nonexistent_project_404(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Unassign Proj"}, headers=h)
    ).json()["data"]["id"]
    r = await c.delete(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects/01BOGUSBOGUSBOGUSBOGUSBOGU", headers=h
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_project_assignment_duplicate_409(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Dup Proj"}, headers=h)
    ).json()["data"]["id"]
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Dup Proj",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    assert (
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", json={"project_id": pid}, headers=h
        )
    ).status_code == 201
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", json={"project_id": pid}, headers=h
    )
    assert r.status_code == 409
