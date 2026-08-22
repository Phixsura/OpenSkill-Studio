"""Integration tests for client brief management."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"br-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Br"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


def _brief_body(**overrides):
    base = {
        "title": f"Brief {uuid.uuid4().hex[:6]}",
        "client_name": "Acme Corp",
        "project_type": "product_visualization",
        "objective": "Create hero images for new product line",
    }
    base.update(overrides)
    return base


# ── CRUD ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_brief(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(), headers=h)
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["client_name"] == "Acme Corp"
    assert d["status"] == "draft"


@pytest.mark.asyncio
async def test_list_briefs(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(title="Alpha"), headers=h)
    await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(title="Beta"), headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/briefs", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 2


@pytest.mark.asyncio
async def test_update_brief(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(), headers=h)).json()[
        "data"
    ]["id"]
    # Update name (no status change)
    r = await c.put(
        f"/api/v1/orgs/{oid}/briefs/{bid}",
        json={"client_name": "Globex"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["client_name"] == "Globex"

    # Transition to a valid next status: draft → open
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/briefs/{bid}",
        json={"status": "open"},
        headers=h,
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["status"] == "open"


@pytest.mark.asyncio
async def test_delete_draft_only(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(), headers=h)).json()[
        "data"
    ]["id"]
    assert (await c.delete(f"/api/v1/orgs/{oid}/briefs/{bid}", headers=h)).status_code == 204
    # non-draft — transition to open first (valid: draft → open)
    bid2 = (await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(), headers=h)).json()[
        "data"
    ]["id"]
    await c.put(f"/api/v1/orgs/{oid}/briefs/{bid2}", json={"status": "open"}, headers=h)
    assert (await c.delete(f"/api/v1/orgs/{oid}/briefs/{bid2}", headers=h)).status_code == 422


@pytest.mark.asyncio
async def test_student_cannot_access_briefs(c):
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )
    r = await c.get(f"/api/v1/orgs/{oid}/briefs", headers=hs)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_cross_org_brief_hidden(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    o1 = await _org(c, h1)
    await _org(c, h2)
    bid = (await c.post(f"/api/v1/orgs/{o1}/briefs", json=_brief_body(), headers=h1)).json()[
        "data"
    ]["id"]
    r = await c.get(f"/api/v1/orgs/{o1}/briefs/{bid}", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_brief_validation(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs",
        json={"title": "X", "client_name": "C", "project_type": "p", "objective": "o"},
        headers=h,
    )
    assert r.status_code == 422  # title too short
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs",
        json=_brief_body(client_website="javascript:alert(1)"),
        headers=h,
    )
    assert r.status_code == 422  # bad URL scheme


# ── Convert Brief to Project ─────────────────────────────


@pytest.mark.asyncio
async def test_convert_brief_to_project(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(), headers=h)).json()[
        "data"
    ]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/convert",
        json={"rubric": [{"criterion": "Quality", "max_score": 100}]},
        headers=h,
    )
    assert r.status_code == 201
    project = r.json()["data"]
    assert project["project_type"] == "ai_visual"
    # brief status should now be active
    brief = (await c.get(f"/api/v1/orgs/{oid}/briefs/{bid}", headers=h)).json()["data"]
    assert brief["status"] == "active"


@pytest.mark.asyncio
async def test_convert_with_cohort(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(), headers=h)).json()[
        "data"
    ]["id"]
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Convert Cohort"}, headers=h)
    ).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/convert",
        json={
            "cohort_id": cid,
            "rubric": [{"criterion": "Q", "max_score": 100}],
            "deadline": "2030-12-01T00:00:00Z",
        },
        headers=h,
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_convert_cross_org_rejected(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    o1 = await _org(c, h1)
    await _org(c, h2)
    bid = (await c.post(f"/api/v1/orgs/{o1}/briefs", json=_brief_body(), headers=h1)).json()[
        "data"
    ]["id"]
    r = await c.post(
        f"/api/v1/orgs/{await _org(c, h2)}/briefs/{bid}/convert",
        json={"rubric": [{"criterion": "Q", "max_score": 100}]},
        headers=h2,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_brief_with_deliverable_specs(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    body = _brief_body(
        deliverable_specs=[
            {"name": "Hero Image", "type": "image", "description": "Main product shot"},
            {"name": "Product Video", "type": "video", "description": "15s clip"},
        ]
    )
    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json=body, headers=h)).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/convert",
        json={"rubric": [{"criterion": "Q", "max_score": 100}]},
        headers=h,
    )
    assert r.status_code == 201
    # project should have been created with deliverables from specs
    pid = r.json()["data"]["id"]
    details = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)).json()["data"]
    assert len(details["deliverables"]) == 2
    assert details["deliverables"][0]["name"] == "Hero Image"


@pytest.mark.asyncio
async def test_brief_status_filter(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(), headers=h)).json()[
        "data"
    ]["id"]
    # Use valid transition: draft → open
    await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "open"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(title="Draft Brief"), headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/briefs?status=open", headers=h)
    assert r.json()["meta"]["total"] == 1


# ── Edge cases ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_brief_title_reslugs(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    bid = (
        await c.post(
            f"/api/v1/orgs/{oid}/briefs", json=_brief_body(title="Original Brief"), headers=h
        )
    ).json()["data"]["id"]
    r = await c.put(
        f"/api/v1/orgs/{oid}/briefs/{bid}", json={"title": "New Brief Title"}, headers=h
    )
    assert r.status_code == 200
    assert "new-brief-title" in r.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_convert_empty_deliverable_specs(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    bid = (
        await c.post(
            f"/api/v1/orgs/{oid}/briefs", json=_brief_body(deliverable_specs=[]), headers=h
        )
    ).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/convert",
        json={"rubric": [{"criterion": "Q", "max_score": 100}]},
        headers=h,
    )
    assert r.status_code == 201
    pid = r.json()["data"]["id"]
    detail = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)).json()["data"]
    assert len(detail["deliverables"]) == 0


@pytest.mark.asyncio
async def test_brief_field_bounds(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(f"/api/v1/orgs/{oid}/briefs", json=_brief_body(title="X" * 400), headers=h)
    assert r.status_code == 422
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs", json=_brief_body(client_name="C" * 300), headers=h
    )
    assert r.status_code == 422
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs", json=_brief_body(objective="O" * 20000), headers=h
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_brief_with_all_fields(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs",
        json=_brief_body(
            client_industry="Tech",
            client_website="https://example.com",
            brand_guidelines="Use blue palette",
            target_audience="Designers",
            tone_and_style="Modern",
            constraints="No red",
            budget_range="$1000-$5000",
            timeline="2 weeks",
            deliverable_specs=[{"name": "Logo", "type": "image"}],
            references=[{"url": "https://example.com/ref"}],
            evaluation_criteria=[{"criterion": "Brand fit", "weight": 0.5}],
        ),
        headers=h,
    )
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["client_industry"] == "Tech"
    assert d["budget_range"] == "$1000-$5000"
    assert len(d["deliverable_specs"]) == 1
    assert len(d["evaluation_criteria"]) == 1
