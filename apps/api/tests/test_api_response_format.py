"""Tests verifying API response format consistency."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"fmt-{uuid.uuid4().hex[:8]}@test.com"


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
async def test_list_response_has_meta(c):
    r = await c.get("/api/v1/marketplace/apps")
    j = r.json()
    assert "data" in j
    assert "meta" in j
    meta = j["meta"]
    assert "total" in meta
    assert "page" in meta
    assert "per_page" in meta
    assert "has_more" in meta
    assert isinstance(meta["total"], int)
    assert isinstance(meta["has_more"], bool)


@pytest.mark.asyncio
async def test_single_response_has_data(c):
    r = await c.get("/api/v1/marketplace/categories")
    assert "data" in r.json()
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_error_response_format(c):
    r = await c.get("/api/v1/marketplace/apps/nonexistent")
    assert r.status_code == 404
    j = r.json()
    assert "error" in j
    assert "code" in j["error"]
    assert "message" in j["error"]


@pytest.mark.asyncio
async def test_validation_error_format(c):
    r = await c.get("/api/v1/marketplace/apps?page=0")
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_auth_error_format(c):
    r = await c.get("/api/v1/developer/accounts/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_created_response_data(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "Fmt"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"fmt-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/accounts", json={
        "display_name": "Fmt Dev", "slug": slug, "support_email": f"{slug}@t.com",
    }, headers=h)
    assert r.status_code == 200
    assert "data" in r.json()
    assert "id" in r.json()["data"]


@pytest.mark.asyncio
async def test_featured_returns_list(c):
    r = await c.get("/api/v1/marketplace/featured")
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_recent_returns_list(c):
    r = await c.get("/api/v1/marketplace/recent")
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_trending_returns_list(c):
    r = await c.get("/api/v1/marketplace/trending")
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_categories_returns_list_of_objects(c):
    r = await c.get("/api/v1/marketplace/categories")
    data = r.json()["data"]
    assert isinstance(data, list)
    assert all(isinstance(cat, dict) for cat in data)
