"""Tests for all observability endpoints."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"obs-{uuid.uuid4().hex[:8]}@test.com"

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
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "Obs"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"obs-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "Obs Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"obsapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "Obs App", "slug": s, "category": "analytics"}, headers=h)
    app_id = r.json()["data"]["id"]
    await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "a" * 64,
    }, headers=h)
    return h, app_id

@pytest.mark.asyncio
async def test_stats(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/stats", headers=h)
    assert r.status_code == 200
    d = r.json()["data"]
    assert "active_installs" in d
    assert "executions_24h" in d

@pytest.mark.asyncio
async def test_health(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/health", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["status"] in ("unknown", "healthy", "degraded", "critical")

@pytest.mark.asyncio
async def test_conformance(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/conformance", headers=h)
    assert r.status_code == 200
    assert "summary" in r.json()["data"]

@pytest.mark.asyncio
async def test_version_adoption(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/version-adoption", headers=h)
    assert r.status_code == 200
    assert "versions" in r.json()["data"]

@pytest.mark.asyncio
async def test_usage(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/usage", headers=h)
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_analytics_summary(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/analytics/summary", headers=h)
    assert r.status_code == 200
    assert "active_installs" in r.json()["data"]

@pytest.mark.asyncio
async def test_analytics_installs(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/analytics/installs", headers=h)
    assert r.status_code == 200
    assert "timeline" in r.json()["data"]

@pytest.mark.asyncio
async def test_analytics_executions(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/analytics/executions", headers=h)
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_webhook_deliveries(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/webhook-deliveries", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 0

@pytest.mark.asyncio
async def test_install_breakdown(c):
    h, app_id = await _app(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/installs/breakdown", headers=h)
    assert r.status_code == 200
    assert "breakdown" in r.json()["data"]
