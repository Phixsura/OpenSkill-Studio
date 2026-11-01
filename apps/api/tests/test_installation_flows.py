"""Installation flow tests — install, upgrade, pin, unpin, rollback, uninstall."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"if-{uuid.uuid4().hex[:8]}@test.com"

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

async def _setup(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "IF"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"if-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "IF Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"ifapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "IF App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "a" * 64,
    }, headers=h)
    v1 = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "2.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "b" * 64,
    }, headers=h)
    v2 = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    return h, app_id, v1, v2, org_id

@pytest.mark.asyncio
async def test_full_install_lifecycle(c):
    h, app_id, v1, v2, org_id = await _setup(c)
    # Install v1
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v1}, headers=h)
    assert r.status_code == 200
    inst_id = r.json()["data"]["id"]
    # Upgrade to v2
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/upgrade", headers=h)
    assert r.json()["data"]["app_version_id"] == v2
    # Pin
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/pin", headers=h)
    assert r.json()["data"]["pinned_version"] is True
    # Unpin
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/unpin", headers=h)
    assert r.json()["data"]["pinned_version"] is False
    # Rollback to v1
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rollback", json={"target_version_id": v1}, headers=h)
    assert r.json()["data"]["app_version_id"] == v1
    # Uninstall
    r = await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}", headers=h)
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_install_twice_rejected(c):
    h, app_id, v1, _, org_id = await _setup(c)
    await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v1}, headers=h)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v1}, headers=h)
    assert r.status_code == 409

@pytest.mark.asyncio
async def test_upgrade_noop_when_latest(c):
    h, app_id, _, v2, org_id = await _setup(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v2}, headers=h)
    inst_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/upgrade", headers=h)
    assert r.json()["data"]["app_version_id"] == v2

@pytest.mark.asyncio
async def test_rollback_wrong_version(c):
    h, app_id, v1, v2, org_id = await _setup(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v1}, headers=h)
    inst_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rollback", json={"target_version_id": "fake"}, headers=h)
    assert r.status_code == 404
