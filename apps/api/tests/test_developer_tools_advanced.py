"""Advanced developer tools endpoint tests."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"dt-{uuid.uuid4().hex[:8]}@test.com"

@pytest_asyncio.fixture
async def c():
    from app.main import app
    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager
    from app.core.database import engine
    @asynccontextmanager
    async def _noop(a): yield
    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()

async def _auth_dev(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "DT"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"dt-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "DT Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    return h

@pytest.mark.asyncio
async def test_event_types_has_categories(c):
    h = await _auth_dev(c)
    r = await c.get("/api/v1/developer/tools/event-types", headers=h)
    cats = r.json()["data"]["categories"]
    assert "submission" in cats
    assert "cohort" in cats
    assert "app" in cats
    assert "marketplace" in cats

@pytest.mark.asyncio
async def test_permissions_has_categories(c):
    h = await _auth_dev(c)
    r = await c.get("/api/v1/developer/tools/permissions", headers=h)
    cats = r.json()["data"]["categories"]
    assert "read" in cats
    assert "write" in cats
    assert "subscribe" in cats

@pytest.mark.asyncio
async def test_surfaces_all_have_ids(c):
    h = await _auth_dev(c)
    r = await c.get("/api/v1/developer/tools/ui-surfaces", headers=h)
    for surface in r.json()["data"]["surfaces"]:
        assert "id" in surface
        assert "label" in surface

@pytest.mark.asyncio
async def test_fixtures_have_event_payloads(c):
    h = await _auth_dev(c)
    r = await c.post("/api/v1/developer/tools/generate-fixtures", headers=h)
    payloads = r.json()["data"]["event_payload"]
    assert "submission.completed" in payloads
    assert "cohort.member_added" in payloads
    assert "pack.published" in payloads

@pytest.mark.asyncio
async def test_validate_valid_manifest(c):
    h = await _auth_dev(c)
    r = await c.post("/api/v1/developer/tools/validate", json={
        "manifest": {"schema_version": "1.0", "app": {"name": "Valid"}, "permissions": ["read:cohorts"]},
    }, headers=h)
    assert r.json()["data"]["valid"] is True

@pytest.mark.asyncio
async def test_validate_invalid_manifest(c):
    h = await _auth_dev(c)
    r = await c.post("/api/v1/developer/tools/validate", json={
        "manifest": {"permissions": ["hack:system"]},
    }, headers=h)
    assert r.json()["data"]["valid"] is False

@pytest.mark.asyncio
async def test_send_test_event(c):
    h = await _auth_dev(c)
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    r = await c.post("/api/v1/developer/tools/send-test-event", json={
        "event_type": "submission.completed", "data": {"test": True}, "org_id": org_id,
    }, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["test"] is True

@pytest.mark.asyncio
async def test_send_invalid_event_type(c):
    h = await _auth_dev(c)
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    r = await c.post("/api/v1/developer/tools/send-test-event", json={
        "event_type": "fake.event", "org_id": org_id,
    }, headers=h)
    assert r.status_code == 422

@pytest.mark.asyncio
async def test_tools_require_auth(c):
    for ep in ["/api/v1/developer/tools/event-types", "/api/v1/developer/tools/permissions", "/api/v1/developer/tools/ui-surfaces"]:
        r = await c.get(ep)
        assert r.status_code == 401

@pytest.mark.asyncio
async def test_validate_requires_auth(c):
    r = await c.post("/api/v1/developer/tools/validate", json={"manifest": {}})
    assert r.status_code == 401
