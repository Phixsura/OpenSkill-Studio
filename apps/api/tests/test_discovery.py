"""Tests for marketplace discovery endpoints — featured, recent, trending."""

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
async def test_featured_apps(c):
    r = await c.get("/api/v1/marketplace/featured")
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_featured_with_limit(c):
    r = await c.get("/api/v1/marketplace/featured?limit=3")
    assert r.status_code == 200
    assert len(r.json()["data"]) <= 3


@pytest.mark.asyncio
async def test_recent_apps(c):
    r = await c.get("/api/v1/marketplace/recent")
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_trending_apps(c):
    r = await c.get("/api/v1/marketplace/trending")
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_trending_with_days(c):
    r = await c.get("/api/v1/marketplace/trending?days=14&limit=5")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_discovery_no_auth_required(c):
    """All discovery endpoints are public."""
    for ep in ["/api/v1/marketplace/featured", "/api/v1/marketplace/recent", "/api/v1/marketplace/trending"]:
        r = await c.get(ep)
        assert r.status_code == 200, f"{ep} should not require auth"


def test_discovery_service_imports():
    from app.services.app_discovery import get_featured_apps, get_recent_apps, get_trending_apps

    assert callable(get_featured_apps)
    assert callable(get_recent_apps)
    assert callable(get_trending_apps)
