"""Tests for review submission endpoints."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"rv-{uuid.uuid4().hex[:8]}@test.com"

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

async def _app_with_version(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "RV"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"rv-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "RV Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"rvapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "RV App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {"name": "RV"}, "permissions": ["read:cohorts"]},
        "content_hash": "a" * 64,
    }, headers=h)
    return h, app_id, r.json()["data"]["id"]

@pytest.mark.asyncio
async def test_submit_review(c):
    h, app_id, v_id = await _app_with_version(c)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/reviews", json={"app_version_id": v_id}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["review_status"] in ("pending", "PENDING")

@pytest.mark.asyncio
async def test_review_has_automated_checks(c):
    h, app_id, v_id = await _app_with_version(c)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/reviews", json={"app_version_id": v_id}, headers=h)
    checks = r.json()["data"]["automated_checks"]
    assert checks is not None
    assert "checks_passed" in checks

@pytest.mark.asyncio
async def test_list_reviews(c):
    h, app_id, v_id = await _app_with_version(c)
    await c.post(f"/api/v1/developer/apps/{app_id}/reviews", json={"app_version_id": v_id}, headers=h)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/reviews", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1

@pytest.mark.asyncio
async def test_review_ownership_required(c):
    h1, app_id, v_id = await _app_with_version(c)
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "X"})
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/developer/apps/{app_id}/reviews", headers=h2)
    assert r.status_code in (403, 404)

@pytest.mark.asyncio
async def test_review_wrong_version(c):
    h, app_id, v_id = await _app_with_version(c)
    r = await c.post(f"/api/v1/developer/apps/{app_id}/reviews", json={"app_version_id": "wrong-version-id"}, headers=h)
    assert r.status_code == 404
