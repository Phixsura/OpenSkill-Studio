"""Final sweep — cross-service integration and response format."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"fs-{uuid.uuid4().hex[:8]}@test.com"

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

@pytest.mark.asyncio
async def test_full_account_app_version_flow(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "FS"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"fs-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/accounts", json={"display_name": "FS Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    assert r.status_code == 200
    s = f"fsapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "FS App", "slug": s, "category": "connector"}, headers=h)
    assert r.status_code == 200
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "a" * 64,
    }, headers=h)
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_marketplace_search_and_category(c):
    r = await c.get("/api/v1/marketplace/apps?q=test&category=connector&page=1&per_page=5")
    assert r.status_code == 200
    assert "data" in r.json()
    assert "meta" in r.json()

@pytest.mark.asyncio
async def test_all_public_endpoints_no_auth(c):
    endpoints = [
        "/api/v1/marketplace/apps",
        "/api/v1/marketplace/categories",
        "/api/v1/marketplace/featured",
        "/api/v1/marketplace/recent",
        "/api/v1/marketplace/trending",
    ]
    for ep in endpoints:
        r = await c.get(ep)
        assert r.status_code == 200, f"{ep} failed"

@pytest.mark.asyncio
async def test_all_auth_endpoints_reject_unauthed(c):
    endpoints = [
        "/api/v1/developer/accounts/me",
        "/api/v1/developer/apps",
        "/api/v1/developer/signing-keys",
        "/api/v1/developer/adapters",
        "/api/v1/developer/sources",
        "/api/v1/developer/tools/event-types",
        "/api/v1/developer/tools/permissions",
        "/api/v1/developer/tools/ui-surfaces",
    ]
    for ep in endpoints:
        r = await c.get(ep)
        assert r.status_code == 401, f"{ep} should require auth"
