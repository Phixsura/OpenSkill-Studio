"""Tests for marketplace categories endpoint."""

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
async def test_list_categories(c):
    """Categories endpoint returns all 7 categories."""
    r = await c.get("/api/v1/marketplace/categories")
    assert r.status_code == 200
    cats = r.json()["data"]
    assert len(cats) == 7
    keys = {cat["key"] for cat in cats}
    assert "connector" in keys
    assert "ui_extension" in keys
    assert "ecosystem_source" in keys


@pytest.mark.asyncio
async def test_categories_no_auth_required(c):
    """Categories endpoint is public."""
    r = await c.get("/api/v1/marketplace/categories")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_categories_have_metadata(c):
    r = await c.get("/api/v1/marketplace/categories")
    cats = r.json()["data"]
    for cat in cats:
        assert "key" in cat
        assert "icon" in cat
        assert "label" in cat
        assert "description" in cat
        assert "app_count" in cat
        assert isinstance(cat["app_count"], int)
