"""Tests for export endpoint authorization and format."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"exp-{uuid.uuid4().hex[:8]}@test.com"

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
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "Exp"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"exp-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "Exp Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"expapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "Exp App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {"name": "Exp"}, "permissions": ["read:cohorts"]},
        "content_hash": "a" * 64, "changelog": "v1",
    }, headers=h)
    v_id = r.json()["data"]["id"]
    return h, app_id, v_id

@pytest.mark.asyncio
async def test_export_has_versions(c):
    h, app_id, _ = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/export", headers=h)
    assert r.json()["data"]["version_count"] == 1
    assert r.json()["data"]["versions"][0]["version"] == "1.0.0"

@pytest.mark.asyncio
async def test_export_has_manifest(c):
    h, app_id, _ = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/export", headers=h)
    v = r.json()["data"]["versions"][0]
    assert v["manifest"]["schema_version"] == "1.0"

@pytest.mark.asyncio
async def test_export_has_changelog(c):
    h, app_id, _ = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/export", headers=h)
    assert r.json()["data"]["versions"][0]["changelog"] == "v1"

@pytest.mark.asyncio
async def test_export_has_app_metadata(c):
    h, app_id, _ = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/export", headers=h)
    app_data = r.json()["data"]["app"]
    assert app_data["name"] == "Exp App"
    assert "slug" in app_data
    assert "category" in app_data

@pytest.mark.asyncio
async def test_export_auth_required(c):
    r = await c.get("/api/v1/developer/apps/fake-id/export")
    assert r.status_code == 401

@pytest.mark.asyncio
async def test_export_ownership_required(c):
    h1, app_id, _ = await _setup(c)
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "Other"})
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/developer/apps/{app_id}/export", headers=h2)
    assert r.status_code == 403

@pytest.mark.asyncio
async def test_export_nonexistent_app(c):
    h, _, _ = await _setup(c)
    r = await c.get("/api/v1/developer/apps/nonexistent-id/export", headers=h)
    assert r.status_code == 404
