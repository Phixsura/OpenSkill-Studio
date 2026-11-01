"""Tests for all public marketplace endpoints (no auth required)."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


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


@pytest.mark.asyncio
async def test_browse_apps(c):
    r = await c.get("/api/v1/marketplace/apps")
    assert r.status_code == 200
    assert "data" in r.json()
    assert "meta" in r.json()


@pytest.mark.asyncio
async def test_browse_apps_with_search(c):
    r = await c.get("/api/v1/marketplace/apps?q=connector")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_browse_apps_with_category(c):
    for cat in ["connector", "analytics", "automation"]:
        r = await c.get(f"/api/v1/marketplace/apps?category={cat}")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_browse_apps_pagination(c):
    r = await c.get("/api/v1/marketplace/apps?page=1&per_page=5")
    assert r.status_code == 200
    assert r.json()["meta"]["per_page"] == 5


@pytest.mark.asyncio
async def test_categories_endpoint(c):
    r = await c.get("/api/v1/marketplace/categories")
    assert r.status_code == 200
    assert len(r.json()["data"]) == 7
    for cat in r.json()["data"]:
        assert all(k in cat for k in ["key", "icon", "label", "description", "app_count"])


@pytest.mark.asyncio
async def test_featured_endpoint(c):
    r = await c.get("/api/v1/marketplace/featured")
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_featured_with_limit(c):
    r = await c.get("/api/v1/marketplace/featured?limit=2")
    assert r.status_code == 200
    assert len(r.json()["data"]) <= 2


@pytest.mark.asyncio
async def test_recent_endpoint(c):
    r = await c.get("/api/v1/marketplace/recent")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_recent_with_limit(c):
    r = await c.get("/api/v1/marketplace/recent?limit=3")
    assert r.status_code == 200
    assert len(r.json()["data"]) <= 3


@pytest.mark.asyncio
async def test_trending_endpoint(c):
    r = await c.get("/api/v1/marketplace/trending")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_trending_with_params(c):
    r = await c.get("/api/v1/marketplace/trending?days=14&limit=5")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_app_detail_not_found(c):
    r = await c.get("/api/v1/marketplace/apps/nonexistent-app-id")
    assert r.status_code == 404
