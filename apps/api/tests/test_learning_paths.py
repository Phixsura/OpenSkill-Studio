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
    r = await c.post("/api/v1/orgs", json={"name": f"LP-{uuid.uuid4().hex[:6]}"}, headers=h)
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
