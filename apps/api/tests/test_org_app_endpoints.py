"""Tests for org-scoped app endpoints."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"oa-{uuid.uuid4().hex[:8]}@test.com"

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

async def _org_install(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "OA"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"oa-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "OA Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"oaapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "OA App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "a" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v_id}, headers=h)
    return h, org_id, ir.json()["data"]["id"], app_id

@pytest.mark.asyncio
async def test_org_installations_list(c):
    h, org_id, inst_id, _ = await _org_install(c)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1

@pytest.mark.asyncio
async def test_org_installation_detail(c):
    h, org_id, inst_id, _ = await _org_install(c)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["id"] == inst_id

@pytest.mark.asyncio
async def test_org_stats(c):
    h, org_id, _, _ = await _org_install(c)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/stats", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["installed_apps"] >= 1

@pytest.mark.asyncio
async def test_org_install_export(c):
    h, org_id, inst_id, _ = await _org_install(c)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/export", headers=h)
    assert r.status_code == 200
    assert "installation" in r.json()["data"]

@pytest.mark.asyncio
async def test_org_non_member_rejected(c):
    h1, org_id, inst_id, _ = await _org_install(c)
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "X"})
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations", headers=h2)
    assert r.status_code in (403, 404)

@pytest.mark.asyncio
async def test_org_wrong_installation(c):
    h, org_id, inst_id, _ = await _org_install(c)
    org2_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org2_id = org2_r.json()["data"]["id"]
    r = await c.get(f"/api/v1/orgs/{org2_id}/apps/installations/{inst_id}", headers=h)
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_uninstall(c):
    h, org_id, inst_id, _ = await _org_install(c)
    r = await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}", headers=h)
    assert r.status_code == 200
