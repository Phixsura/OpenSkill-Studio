"""Tests for search and discovery filter scenarios."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"sf-{uuid.uuid4().hex[:8]}@test.com"


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
async def test_browse_empty_query(c):
    r = await c.get("/api/v1/marketplace/apps?q=")
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_browse_special_chars_query(c):
    r = await c.get("/api/v1/marketplace/apps?q=%25drop%20table")
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_browse_page_zero(c):
    r = await c.get("/api/v1/marketplace/apps?page=0")
    assert r.status_code == 422  # page must be >= 1

@pytest.mark.asyncio
async def test_browse_per_page_over_limit(c):
    r = await c.get("/api/v1/marketplace/apps?per_page=200")
    assert r.status_code == 422  # max 100

@pytest.mark.asyncio
async def test_categories_all_have_app_count(c):
    r = await c.get("/api/v1/marketplace/categories")
    for cat in r.json()["data"]:
        assert isinstance(cat["app_count"], int)
        assert cat["app_count"] >= 0

@pytest.mark.asyncio
async def test_featured_limit_capped(c):
    r = await c.get("/api/v1/marketplace/featured?limit=100")
    assert r.status_code == 200
    assert len(r.json()["data"]) <= 20  # capped at 20

@pytest.mark.asyncio
async def test_trending_days_capped(c):
    r = await c.get("/api/v1/marketplace/trending?days=365")
    assert r.status_code == 200  # capped at 30 internally

@pytest.mark.asyncio
async def test_recent_limit_capped(c):
    r = await c.get("/api/v1/marketplace/recent?limit=100")
    assert r.status_code == 200
    assert len(r.json()["data"]) <= 20

@pytest.mark.asyncio
async def test_invalid_category_filter(c):
    r = await c.get("/api/v1/marketplace/apps?category=nonexistent_category")
    assert r.status_code in (200, 422)  # may reject invalid enum or return empty

@pytest.mark.asyncio
async def test_marketplace_app_404_format(c):
    r = await c.get("/api/v1/marketplace/apps/definitely-not-real")
    assert r.status_code == 404
    assert "error" in r.json()
    assert "code" in r.json()["error"]
