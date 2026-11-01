"""Tests for analytics endpoints and service."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"ana-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from app.main import app

    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager

    from app.core.database import engine

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


async def _setup(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Ana"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"ana-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Ana Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    app_slug = f"anaapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Ana App", "slug": app_slug, "category": "analytics"},
        headers=h,
    )
    return h, r.json()["data"]


@pytest.mark.asyncio
async def test_analytics_summary(c):
    h, app = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app['id']}/analytics/summary", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["active_installs"] == 0
    assert data["versions"] == 0
    assert data["executions_24h"] == 0


@pytest.mark.asyncio
async def test_analytics_install_timeline(c):
    h, app = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app['id']}/analytics/installs?days=30", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert isinstance(data["timeline"], list)
    assert data["days"] == 30


@pytest.mark.asyncio
async def test_analytics_execution_timeline(c):
    h, app = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app['id']}/analytics/executions?days=7", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert isinstance(data["timeline"], list)


@pytest.mark.asyncio
async def test_analytics_requires_ownership(c):
    h1, app = await _setup(c)
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/developer/apps/{app['id']}/analytics/summary", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_analytics_with_installs(c):
    h, app = await _setup(c)
    # Create version + install
    r = await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "a" * 64,
        },
        headers=h,
    )
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app["id"], "app_version_id": v_id},
        headers=h,
    )

    r = await c.get(f"/api/v1/developer/apps/{app['id']}/analytics/summary", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["active_installs"] == 1
    assert r.json()["data"]["installs_this_week"] >= 1
    assert r.json()["data"]["versions"] == 1

    # Install timeline should have data
    r = await c.get(f"/api/v1/developer/apps/{app['id']}/analytics/installs", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]["timeline"]) >= 1


def test_analytics_service_imports():
    from app.services.app_analytics import (
        get_app_summary_metrics,
        get_execution_timeline,
        get_install_timeline,
        get_top_orgs,
    )

    assert callable(get_install_timeline)
    assert callable(get_execution_timeline)
    assert callable(get_top_orgs)
    assert callable(get_app_summary_metrics)
