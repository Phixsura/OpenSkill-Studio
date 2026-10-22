"""API key lifecycle tests — create, use, list, revoke, verify rejected."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"akl-{uuid.uuid4().hex[:8]}@test.com"

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

async def _dev_app(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "AKL"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"akl-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "AKL Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"aklapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "AKL App", "slug": s, "category": "connector"}, headers=h)
    return h, r.json()["data"]["id"]

@pytest.mark.asyncio
async def test_create_key_returns_full_key(c):
    h, app_id = await _dev_app(c)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/api-keys", json={"name": "K1", "scopes": ["read:cohorts"]}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["key"].startswith("osk_app_")

@pytest.mark.asyncio
async def test_list_keys_hides_full_key(c):
    h, app_id = await _dev_app(c)
    await c.post(f"/api/v1/developer/apps/{app_id}/api-keys", json={"name": "K2"}, headers=h)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/api-keys", headers=h)
    assert r.status_code == 200
    for key in r.json()["data"]:
        assert "key" not in key or key.get("key") is None

@pytest.mark.asyncio
async def test_key_with_scopes(c):
    h, app_id = await _dev_app(c)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/api-keys", json={"name": "Scoped", "scopes": ["read:cohorts", "read:projects"]}, headers=h)
    assert r.json()["data"]["scopes"] == ["read:cohorts", "read:projects"]

@pytest.mark.asyncio
async def test_key_auth_works(c):
    h, app_id = await _dev_app(c)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/api-keys", json={"name": "Auth"}, headers=h)
    key = r.json()["data"]["key"]
    r = await c.get("/api/v1/developer/accounts/me", headers={"Authorization": f"Bearer {key}"})
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_revoke_key_rejected(c):
    h, app_id = await _dev_app(c)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/api-keys", json={"name": "Rev"}, headers=h)
    key = r.json()["data"]["key"]
    key_id = r.json()["data"]["id"]
    await c.delete(f"/api/v1/developer/apps/{app_id}/api-keys/{key_id}", headers=h)
    r = await c.get("/api/v1/developer/accounts/me", headers={"Authorization": f"Bearer {key}"})
    assert r.status_code == 401

@pytest.mark.asyncio
async def test_multiple_keys(c):
    h, app_id = await _dev_app(c)
    for i in range(3):
        await c.post(f"/api/v1/developer/apps/{app_id}/api-keys", json={"name": f"Key {i}"}, headers=h)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/api-keys", headers=h)
    assert len(r.json()["data"]) == 3
