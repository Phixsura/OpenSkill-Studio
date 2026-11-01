"""Tests for platform admin endpoints and app search."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"admin-{uuid.uuid4().hex[:8]}@test.com"


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


async def _setup_dev_with_app(c):
    """Create user + dev account + published app."""
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Admin"},
    )
    d = r.json()
    h = {"Authorization": f"Bearer {d['access_token']}"}

    slug = f"adm-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Admin Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    app_slug = f"admapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Admin App", "slug": app_slug, "category": "analytics", "description": "Analytics tool"},
        headers=h,
    )
    return h, r.json()["data"]


# ── Search Service ───────────────────────────────────────


def test_search_service_importable():
    """Verify search service is importable and callable."""
    from app.services.app_search import search_marketplace_apps

    assert callable(search_marketplace_apps)


# ── Marketplace API ──────────────────────────────────────


@pytest.mark.asyncio
async def test_marketplace_browse_with_pagination(c):
    r = await c.get("/api/v1/marketplace/apps?page=1&per_page=5")
    assert r.status_code == 200
    data = r.json()
    assert "data" in data
    assert "meta" in data
    assert data["meta"]["page"] == 1
    assert data["meta"]["per_page"] == 5


@pytest.mark.asyncio
async def test_marketplace_browse_all_categories(c):
    categories = [
        "connector", "workflow_adapter", "ui_extension",
        "analytics", "automation", "content_pack", "ecosystem_source",
    ]
    for cat in categories:
        r = await c.get(f"/api/v1/marketplace/apps?category={cat}")
        assert r.status_code == 200, f"Category '{cat}' browse failed"


@pytest.mark.asyncio
async def test_marketplace_search_query(c):
    r = await c.get("/api/v1/marketplace/apps?q=test&per_page=10")
    assert r.status_code == 200


# ── OAuth Flow ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_oauth_authorize_missing_app(c):
    h, _ = await _setup_dev_with_app(c)
    r = await c.get(
        "/api/v1/oauth/authorize?client_id=nonexistent&redirect_uri=https://x.com/cb&scope=read:cohorts&state=test",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["error"] == "invalid_client"


@pytest.mark.asyncio
async def test_oauth_token_wrong_secret(c):
    r = await c.post(
        "/api/v1/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": "fake-code",
            "client_id": "osk_fake",
            "client_secret": "wrong",
        },
    )
    assert r.status_code == 200
    assert r.json()["data"]["error"] == "invalid_client"


# ── App State Machine ────────────────────────────────────


@pytest.mark.asyncio
async def test_draft_cannot_publish(c):
    h, app = await _setup_dev_with_app(c)
    r = await c.post(f"/api/v1/developer/apps/{app['id']}/publish", headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_draft_cannot_deprecate(c):
    h, app = await _setup_dev_with_app(c)
    r = await c.post(f"/api/v1/developer/apps/{app['id']}/deprecate", headers=h)
    assert r.status_code == 422


# ── Error Responses ──────────────────────────────────────


@pytest.mark.asyncio
async def test_get_nonexistent_app(c):
    h, _ = await _setup_dev_with_app(c)
    r = await c.get("/api/v1/developer/apps/nonexistent-id", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_version(c):
    h, app = await _setup_dev_with_app(c)
    r = await c.get(f"/api/v1/developer/apps/{app['id']}/versions/nonexistent", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_installation(c):
    h, _ = await _setup_dev_with_app(c)
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/nonexistent", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_unauthenticated_developer_endpoints(c):
    """Developer endpoints require auth."""
    r = await c.get("/api/v1/developer/accounts/me")
    assert r.status_code == 401

    r = await c.get("/api/v1/developer/apps")
    assert r.status_code == 401

    r = await c.get("/api/v1/developer/signing-keys")
    assert r.status_code == 401
