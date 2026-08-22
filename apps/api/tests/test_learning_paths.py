"""Integration tests for learning paths — CRUD, items, cohort assignment."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"path-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Path"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


async def _skill(c, h, oid, name="Path Skill"):
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"C-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    return (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": name, "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]


async def _project(c, h, oid, name="Path Project"):
    pid = (await c.post(f"/api/v1/orgs/{oid}/projects", json={
        "title": name, "description": "d" * 10, "instructions": "i" * 10,
        "rubric": [{"criterion": "Q", "max_score": 100}],
    }, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    return pid


# ═══════════════ Path CRUD ═══════════════


@pytest.mark.asyncio
async def test_create_path(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(f"/api/v1/orgs/{oid}/paths", json={
        "name": "AI E-commerce Creator Path",
        "description": "Full training track",
        "estimated_minutes": 480,
    }, headers=h)
    assert r.status_code == 201
    assert r.json()["data"]["name"] == "AI E-commerce Creator Path"
    assert r.json()["data"]["status"] == "draft"


@pytest.mark.asyncio
async def test_list_paths(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Path A"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Path B"}, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/paths", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 2


@pytest.mark.asyncio
async def test_update_path(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Old"}, headers=h)).json()["data"]["id"]
    r = await c.put(f"/api/v1/orgs/{oid}/paths/{pid}", json={"name": "New"}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "New"


@pytest.mark.asyncio
async def test_delete_path(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Del"}, headers=h)).json()["data"]["id"]
    r = await c.delete(f"/api/v1/orgs/{oid}/paths/{pid}", headers=h)
    assert r.status_code == 204
    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}", headers=h)
    assert r.status_code == 404


# ═══════════════ Items ═══════════════


@pytest.mark.asyncio
async def test_add_skill_item(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Items"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)
    r = await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": sid, "sort_order": 0,
    }, headers=h)
    assert r.status_code == 201
    assert r.json()["data"]["item_type"] == "skill"


@pytest.mark.asyncio
async def test_add_project_item(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Proj Items"}, headers=h)).json()["data"]["id"]
    proj_id = await _project(c, h, oid)
    r = await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "project", "project_id": proj_id, "sort_order": 1,
    }, headers=h)
    assert r.status_code == 201
    assert r.json()["data"]["item_type"] == "project"


@pytest.mark.asyncio
async def test_add_section_item(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Sec Items"}, headers=h)).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "section", "section_title": "Fundamentals",
    }, headers=h)
    assert r.status_code == 201
    assert r.json()["data"]["item_type"] == "section"


@pytest.mark.asyncio
async def test_list_items_ordered(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Ordered"}, headers=h)).json()["data"]["id"]
    s1 = await _skill(c, h, oid, "First")
    s2 = await _skill(c, h, oid, "Second")
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={"item_type": "skill", "skill_id": s2, "sort_order": 1}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={"item_type": "skill", "skill_id": s1, "sort_order": 0}, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}/items", headers=h)
    assert r.status_code == 200
    items = r.json()["data"]
    assert len(items) == 2
    assert items[0]["sort_order"] == 0
    assert items[1]["sort_order"] == 1


@pytest.mark.asyncio
async def test_remove_item(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Remove"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)
    item = (await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={"item_type": "skill", "skill_id": sid}, headers=h)).json()["data"]
    r = await c.delete(f"/api/v1/orgs/{oid}/paths/{pid}/items/{item['id']}", headers=h)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_cross_org_skill_rejected(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/paths", json={"name": "XOrg"}, headers=h1)).json()["data"]["id"]
    sid = await _skill(c, h2, oid2)
    r = await c.post(f"/api/v1/orgs/{oid1}/paths/{pid}/items", json={"item_type": "skill", "skill_id": sid}, headers=h1)
    assert r.status_code == 404


# ═══════════════ Cohort Assignment ═══════════════


@pytest.mark.asyncio
async def test_assign_path_to_cohort(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Assign"}, headers=h)).json()["data"]["id"]
    # Publish path first
    await c.put(f"/api/v1/orgs/{oid}/paths/{pid}", json={"status": "published"}, headers=h)
    # Create cohort
    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "PathCohort"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths", json={"path_id": pid}, headers=h)
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_assign_draft_path_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Draft Path"}, headers=h)).json()["data"]["id"]
    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "DraftCohort"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths", json={"path_id": pid}, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_list_cohort_paths(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "ListCP"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/paths/{pid}", json={"status": "published"}, headers=h)
    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "ListCohort"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths", json={"path_id": pid}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1


# ═══════════════ Progress ═══════════════


@pytest.mark.asyncio
async def test_path_progress(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Progress"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={"item_type": "skill", "skill_id": sid}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}/my-progress", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total_required"] == 1
    assert data["completed"] == 0
    assert data["pct"] == 0


# ═══════════════ Cross-org isolation ═══════════════


@pytest.mark.asyncio
async def test_cross_org_path_access(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/paths", json={"name": "Private"}, headers=h1)).json()["data"]["id"]
    r = await c.get(f"/api/v1/orgs/{oid2}/paths/{pid}", headers=h2)
    assert r.status_code == 404


# ═══════════════ Validation Errors ═══════════════


@pytest.mark.asyncio
async def test_add_skill_item_missing_skill_id(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "MissingSkill"}, headers=h)).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill",
    }, headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "MISSING_SKILL_ID"


@pytest.mark.asyncio
async def test_add_project_item_missing_project_id(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "MissingProj"}, headers=h)).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "project",
    }, headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "MISSING_PROJECT_ID"


@pytest.mark.asyncio
async def test_add_section_item_missing_title(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "MissingSec"}, headers=h)).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "section",
    }, headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "MISSING_TITLE"


@pytest.mark.asyncio
async def test_add_cross_org_project_item(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/paths", json={"name": "XOrgProj"}, headers=h1)).json()["data"]["id"]
    proj_id = await _project(c, h2, oid2)
    r = await c.post(f"/api/v1/orgs/{oid1}/paths/{pid}/items", json={
        "item_type": "project", "project_id": proj_id,
    }, headers=h1)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "PROJECT_NOT_FOUND"


@pytest.mark.asyncio
async def test_remove_item_not_found(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "RemoveNF"}, headers=h)).json()["data"]["id"]
    fake_id = "01JFAKE00000000000000FAKE"
    r = await c.delete(f"/api/v1/orgs/{oid}/paths/{pid}/items/{fake_id}", headers=h)
    assert r.status_code == 404


# ═══════════════ Unassign ═══════════════


@pytest.mark.asyncio
async def test_unassign_from_cohort(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Unassign"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/paths/{pid}", json={"status": "published"}, headers=h)
    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "UnCohort"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths", json={"path_id": pid}, headers=h)

    r = await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths/{pid}", headers=h)
    assert r.status_code == 204

    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 0


@pytest.mark.asyncio
async def test_unassign_not_assigned(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "NotAssigned"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/paths/{pid}", json={"status": "published"}, headers=h)
    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "NACohort"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)

    r = await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths/{pid}", headers=h)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_ASSIGNED"


@pytest.mark.asyncio
async def test_assign_already_assigned(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Dup"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/paths/{pid}", json={"status": "published"}, headers=h)
    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "DupCohort"}, headers=h)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths", json={"path_id": pid}, headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/paths", json={"path_id": pid}, headers=h)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ALREADY_ASSIGNED"


@pytest.mark.asyncio
async def test_assign_cross_org_cohort_idor(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/paths", json={"name": "IDORPath"}, headers=h1)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid1}/paths/{pid}", json={"status": "published"}, headers=h1)
    cid = (await c.post(f"/api/v1/orgs/{oid2}/cohorts", json={"name": "IDORCohort"}, headers=h2)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid2}/cohorts/{cid}", json={"status": "active"}, headers=h2)

    r = await c.post(f"/api/v1/orgs/{oid1}/cohorts/{cid}/paths", json={"path_id": pid}, headers=h1)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "COHORT_NOT_FOUND"


# ═══════════════ Progress Edge Cases ═══════════════


@pytest.mark.asyncio
async def test_path_progress_empty_path(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Empty"}, headers=h)).json()["data"]["id"]
    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}/my-progress", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["pct"] == 0
    assert data["total_required"] == 0


@pytest.mark.asyncio
async def test_path_progress_section_only(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "SecOnly"}, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "section", "section_title": "Intro",
    }, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "section", "section_title": "Advanced",
    }, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}/my-progress", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["pct"] == 0


@pytest.mark.asyncio
async def test_path_progress_locked_item(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Locked"}, headers=h)).json()["data"]["id"]
    s1 = await _skill(c, h, oid, "Lock1")
    s2 = await _skill(c, h, oid, "Lock2")
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": s1, "sort_order": 0,
    }, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": s2, "sort_order": 1,
    }, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}/my-progress", headers=h)
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert items[0]["status"] == "available"
    assert items[1]["status"] == "locked"


@pytest.mark.asyncio
async def test_path_progress_immediate_unlock(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Immediate"}, headers=h)).json()["data"]["id"]
    s1 = await _skill(c, h, oid, "Imm1")
    s2 = await _skill(c, h, oid, "Imm2")
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": s1, "sort_order": 0,
    }, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": s2, "sort_order": 1, "unlock_rule": "immediate",
    }, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}/my-progress", headers=h)
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert items[1]["status"] == "available"


@pytest.mark.asyncio
async def test_path_progress_optional_not_counted(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Optional"}, headers=h)).json()["data"]["id"]
    s1 = await _skill(c, h, oid, "Req1")
    s2 = await _skill(c, h, oid, "Opt1")
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": s1, "sort_order": 0, "required": True,
    }, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": s2, "sort_order": 1, "required": False,
    }, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}/my-progress", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["total_required"] == 1


# ═══════════════ IDOR + RBAC ═══════════════


@pytest.mark.asyncio
async def test_cross_org_path_update_idor(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/paths", json={"name": "Private"}, headers=h1)).json()["data"]["id"]
    r = await c.put(f"/api/v1/orgs/{oid2}/paths/{pid}", json={"name": "Hacked"}, headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_cross_org_path_delete_idor(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/paths", json={"name": "Private"}, headers=h1)).json()["data"]["id"]
    r = await c.delete(f"/api/v1/orgs/{oid2}/paths/{pid}", headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_cross_org_path_add_item(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/paths", json={"name": "Private"}, headers=h1)).json()["data"]["id"]
    sid = await _skill(c, h2, oid2)
    r = await c.post(f"/api/v1/orgs/{oid2}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": sid,
    }, headers=h2)
    assert r.status_code in (403, 404)


@pytest.mark.asyncio
async def test_cross_org_path_remove_item(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/paths", json={"name": "Private"}, headers=h1)).json()["data"]["id"]
    sid = await _skill(c, h1, oid1)
    item = (await c.post(f"/api/v1/orgs/{oid1}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": sid,
    }, headers=h1)).json()["data"]
    r = await c.delete(f"/api/v1/orgs/{oid2}/paths/{pid}/items/{item['id']}", headers=h2)
    assert r.status_code in (403, 404)


# ═══════════════ Item wrong path ═══════════════


@pytest.mark.asyncio
async def test_remove_item_wrong_path(c):
    """Deleting an item from path A via path B returns 404."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    path_a = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "PathA"}, headers=h)).json()["data"]["id"]
    path_b = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "PathB"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)
    item = (await c.post(f"/api/v1/orgs/{oid}/paths/{path_a}/items", json={
        "item_type": "skill", "skill_id": sid,
    }, headers=h)).json()["data"]

    r = await c.delete(f"/api/v1/orgs/{oid}/paths/{path_b}/items/{item['id']}", headers=h)
    assert r.status_code == 404


# ═══════════════ Cohort IDOR ═══════════════


@pytest.mark.asyncio
async def test_unassign_cross_org_cohort_idor(c):
    """Unassigning with a cross-org cohort returns 404."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    pid = (await c.post(f"/api/v1/orgs/{oid1}/paths", json={"name": "UnIDOR"}, headers=h1)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid1}/paths/{pid}", json={"status": "published"}, headers=h1)

    cid = (await c.post(f"/api/v1/orgs/{oid2}/cohorts", json={"name": "XOrgCohort"}, headers=h2)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid2}/cohorts/{cid}", json={"status": "active"}, headers=h2)

    r = await c.delete(f"/api/v1/orgs/{oid1}/cohorts/{cid}/paths/{pid}", headers=h1)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "COHORT_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_cohort_paths_cross_org_idor(c):
    """Listing paths with a cross-org cohort returns 404."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    cid = (await c.post(f"/api/v1/orgs/{oid2}/cohorts", json={"name": "XListCohort"}, headers=h2)).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid2}/cohorts/{cid}", json={"status": "active"}, headers=h2)

    r = await c.get(f"/api/v1/orgs/{oid1}/cohorts/{cid}/paths", headers=h1)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "COHORT_NOT_FOUND"


# ═══════════════ Student RBAC ═══════════════


@pytest.mark.asyncio
async def test_student_cannot_create_path(c):
    """Student role cannot create a learning path."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Sneaky Path"}, headers=hs)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_update_path(c):
    """Student role cannot update a learning path."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "StuUpd Path"}, headers=h)).json()["data"]["id"]

    r = await c.put(f"/api/v1/orgs/{oid}/paths/{pid}", json={"name": "Nope"}, headers=hs)
    assert r.status_code == 403


# ═══════════════ List excludes archived ═══════════════


@pytest.mark.asyncio
async def test_list_paths_excludes_archived(c):
    """Deleted (archived) paths must not appear in list results."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Archive Me"}, headers=h)).json()["data"]["id"]
    await c.delete(f"/api/v1/orgs/{oid}/paths/{pid}", headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/paths", headers=h)
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()["data"]]
    assert pid not in ids


# ═══════════════ Invalid item_type ═══════════════


@pytest.mark.asyncio
async def test_add_item_invalid_type(c):
    """item_type='quiz' is not a valid PathItemType → 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "InvalidType"}, headers=h)).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "quiz",
    }, headers=h)
    assert r.status_code == 422


# ═══════════════ Progress pct rounding ═══════════════


@pytest.mark.asyncio
async def test_path_progress_pct_rounds(c):
    """3 required skill items, 1 completed → pct=33."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "PctRound"}, headers=h)).json()["data"]["id"]

    # Create 3 skills, each with an MCQ exercise, add all to path
    exercise_ids = []
    for i in range(3):
        cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"PctCat-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
        sid = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
            "name": f"PctSkill{i}", "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
        }, headers=h)).json()["data"]["id"]
        ex = (await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/exercises", json={
            "title": f"MCQ-{i}", "description": "test", "type": "multiple_choice",
            "config": {"choices": ["A", "B"], "correct": ["A"]}, "max_score": 100,
        }, headers=h)).json()["data"]["id"]
        exercise_ids.append(ex)
        await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
            "item_type": "skill", "skill_id": sid, "sort_order": i, "required": True,
        }, headers=h)

    # Complete only the first skill by submitting correct MCQ answer
    await c.post(f"/api/v1/orgs/{oid}/exercises/{exercise_ids[0]}/attempts", json={
        "answer": {"selected": ["A"]},
    }, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}/my-progress", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["pct"] == 33


# ═══════════════ Mixed sections and skills ═══════════════


@pytest.mark.asyncio
async def test_path_progress_mixed_sections_skills(c):
    """Path with section + 2 skill items — verify all types render correctly."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Mixed"}, headers=h)).json()["data"]["id"]

    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "section", "section_title": "Module 1", "sort_order": 0,
    }, headers=h)
    s1 = await _skill(c, h, oid, "MixedSkill1")
    s2 = await _skill(c, h, oid, "MixedSkill2")
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": s1, "sort_order": 1,
    }, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/paths/{pid}/items", json={
        "item_type": "skill", "skill_id": s2, "sort_order": 2,
    }, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/paths/{pid}/my-progress", headers=h)
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert len(items) == 3
    assert items[0]["type"] == "section"
    assert items[0]["title"] == "Module 1"
    assert items[1]["type"] == "skill"
    assert items[2]["type"] == "skill"


# ═══════════════ Name validation ═══════════════


@pytest.mark.asyncio
async def test_create_path_name_too_short(c):
    """name='X' is below the 2-char minimum → 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "X"}, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_path_name_too_long(c):
    """name='X'*201 exceeds 200-char maximum → 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "X" * 201}, headers=h)
    assert r.status_code == 422


# ═══════════════ Invalid status ═══════════════


@pytest.mark.asyncio
async def test_update_path_invalid_status(c):
    """status='active' is not in {draft, published, archived} → 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "StatTest"}, headers=h)).json()["data"]["id"]
    r = await c.put(f"/api/v1/orgs/{oid}/paths/{pid}", json={"status": "active"}, headers=h)
    assert r.status_code == 422
