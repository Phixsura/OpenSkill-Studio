"""Security boundary tests — verify auth, IDOR, and cross-tenant protections."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"sec-{uuid.uuid4().hex[:8]}@test.com"


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


async def _two_users(c):
    """Create two separate users with dev accounts and apps."""
    # User 1
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "User1"},
    )
    h1 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug1 = f"u1-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Dev1", "slug": slug1, "support_email": f"{slug1}@t.com"},
        headers=h1,
    )
    app_slug1 = f"a1-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "App1", "slug": app_slug1, "category": "connector"},
        headers=h1,
    )
    app1_id = r.json()["data"]["id"]

    # User 2
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "User2"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug2 = f"u2-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Dev2", "slug": slug2, "support_email": f"{slug2}@t.com"},
        headers=h2,
    )

    return h1, app1_id, h2


# ── Cross-user protection ───────────────────────────────


@pytest.mark.asyncio
async def test_user2_cannot_view_user1_app_stats(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.get(f"/api/v1/developer/apps/{app1_id}/stats", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user2_cannot_view_user1_app_health(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.get(f"/api/v1/developer/apps/{app1_id}/health", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user2_cannot_view_user1_conformance(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.get(f"/api/v1/developer/apps/{app1_id}/conformance", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user2_cannot_view_user1_analytics(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.get(f"/api/v1/developer/apps/{app1_id}/analytics/summary", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user2_cannot_create_version_on_user1_app(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.post(
        f"/api/v1/developer/apps/{app1_id}/versions",
        json={
            "version": "9.9.9",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "e" * 64,
        },
        headers=h2,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user2_cannot_submit_user1_app_for_review(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.post(f"/api/v1/developer/apps/{app1_id}/submit", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user2_cannot_create_api_key_for_user1_app(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.post(
        f"/api/v1/developer/apps/{app1_id}/api-keys",
        json={"name": "Stolen Key"},
        headers=h2,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user2_cannot_view_user1_webhook_deliveries(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.get(f"/api/v1/developer/apps/{app1_id}/webhook-deliveries", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user2_cannot_view_user1_usage(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.get(f"/api/v1/developer/apps/{app1_id}/usage", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user2_cannot_deprecation_notice_user1_app(c):
    h1, app1_id, h2 = await _two_users(c)
    r = await c.post(
        f"/api/v1/developer/apps/{app1_id}/deprecation-notice",
        json={"message": "Hacked"},
        headers=h2,
    )
    assert r.status_code == 403


# ── Cross-org installation protection ────────────────────


@pytest.mark.asyncio
async def test_cannot_install_in_non_member_org(c):
    h1, app1_id, h2 = await _two_users(c)
    # User1 creates org
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h1)
    org_id = org_r.json()["data"]["id"]
    # Create version
    r = await c.post(
        f"/api/v1/developer/apps/{app1_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "f" * 64,
        },
        headers=h1,
    )
    v_id = r.json()["data"]["id"]
    # User2 tries to install in User1's org
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app1_id, "app_version_id": v_id},
        headers=h2,
    )
    assert r.status_code == 403
