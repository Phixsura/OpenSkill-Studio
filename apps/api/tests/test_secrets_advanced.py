"""Advanced secret management tests."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"sec-{uuid.uuid4().hex[:8]}@test.com"

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

async def _installed(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "Sec"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"sec-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "Sec Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"secapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "Sec App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "a" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v_id}, headers=h)
    return h, org_id, ir.json()["data"]["id"]

@pytest.mark.asyncio
async def test_set_secret(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.put(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", json={"key": "API_KEY", "value": "secret123", "description": "Main key"}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["key"] == "API_KEY"

@pytest.mark.asyncio
async def test_upsert_secret(c):
    h, org_id, inst_id = await _installed(c)
    await c.put(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", json={"key": "UPS_KEY", "value": "v1"}, headers=h)
    r = await c.put(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", json={"key": "UPS_KEY", "value": "v2", "description": "Updated"}, headers=h)
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_list_secrets_no_values(c):
    h, org_id, inst_id = await _installed(c)
    await c.put(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", json={"key": "HIDDEN", "value": "top-secret"}, headers=h)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", headers=h)
    for s in r.json()["data"]:
        assert "value" not in s
        assert "encrypted_value" not in s

@pytest.mark.asyncio
async def test_delete_secret(c):
    h, org_id, inst_id = await _installed(c)
    await c.put(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", json={"key": "DEL_KEY", "value": "temp"}, headers=h)
    r = await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets/DEL_KEY", headers=h)
    assert r.status_code == 200
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", headers=h)
    assert not any(s["key"] == "DEL_KEY" for s in r.json()["data"])

@pytest.mark.asyncio
async def test_multiple_secrets(c):
    h, org_id, inst_id = await _installed(c)
    for key in ["KEY_A", "KEY_B", "KEY_C"]:
        await c.put(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", json={"key": key, "value": f"v-{key}"}, headers=h)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", headers=h)
    assert len(r.json()["data"]) == 3

@pytest.mark.asyncio
async def test_secret_description(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.put(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", json={"key": "DESC_KEY", "value": "v", "description": "My description"}, headers=h)
    assert r.json()["data"]["description"] == "My description"
