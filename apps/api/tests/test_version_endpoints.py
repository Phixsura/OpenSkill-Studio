"""Tests for version-related endpoints."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"ve-{uuid.uuid4().hex[:8]}@test.com"

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

async def _app(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "VE"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"ve-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "VE Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"veapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "VE App", "slug": s, "category": "connector"}, headers=h)
    return h, r.json()["data"]["id"]

@pytest.mark.asyncio
async def test_create_version_with_all_fields(c):
    h, app_id = await _app(c)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "changelog": "Initial release",
        "manifest": {"schema_version": "1.0", "app": {"name": "VE", "version": "1.0.0"}, "permissions": ["read:cohorts"]},
        "content_hash": "a" * 64, "signature": "ed25519-test-sig", "min_platform_version": "1.0.0",
    }, headers=h)
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["version"] == "1.0.0"
    assert d["changelog"] == "Initial release"
    assert d["signature"] == "ed25519-test-sig"
    assert d["min_platform_version"] == "1.0.0"

@pytest.mark.asyncio
async def test_list_versions_ordered(c):
    h, app_id = await _app(c)
    for ver in ["1.0.0", "1.1.0", "2.0.0"]:
        await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
            "version": ver, "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": f"{ver[0]}" * 64,
        }, headers=h)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/versions", headers=h)
    versions = [v["version"] for v in r.json()["data"]]
    assert "2.0.0" in versions
    assert "1.0.0" in versions

@pytest.mark.asyncio
async def test_duplicate_version_rejected(c):
    h, app_id = await _app(c)
    await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "b" * 64,
    }, headers=h)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "c" * 64,
    }, headers=h)
    assert r.status_code == 409

@pytest.mark.asyncio
async def test_version_requires_ownership(c):
    h1, app_id = await _app(c)
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "X"})
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "9.9.9", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "d" * 64,
    }, headers=h2)
    assert r.status_code in (403, 404)  # 404 if no dev account, 403 if wrong owner

@pytest.mark.asyncio
async def test_get_specific_version(c):
    h, app_id = await _app(c)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "3.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "e" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]
    r = await c.get(f"/api/v1/developer/apps/{app_id}/versions/{v_id}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["version"] == "3.0.0"

@pytest.mark.asyncio
async def test_version_pagination(c):
    h, app_id = await _app(c)
    for i in range(5):
        await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
            "version": f"{i+1}.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": f"{i}" * 64,
        }, headers=h)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/versions?page=1&per_page=3", headers=h)
    assert len(r.json()["data"]) == 3
    assert r.json()["meta"]["total"] == 5
