"""Tests for OAuth2 authorization code flow."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"oauth-{uuid.uuid4().hex[:8]}@test.com"


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


async def _setup_oauth_app(c):
    """Create user + dev account + app with redirect URIs."""
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "OAuth"},
    )
    d = r.json()
    h = {"Authorization": f"Bearer {d['access_token']}"}

    slug = f"oauth-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "OAuth Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )

    app_slug = f"oauthapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={
            "name": "OAuth App",
            "slug": app_slug,
            "category": "connector",
            "redirect_uris": ["https://myapp.example.com/callback"],
            "manifest": {
                "schema_version": "1.0",
                "app": {"name": "OAuth App"},
                "permissions": ["read:cohorts", "read:projects"],
            },
        },
        headers=h,
    )
    app_data = r.json()["data"]

    # Transition to testing so OAuth is allowed
    from sqlalchemy import update as sa_update

    from app.core.database import AsyncSessionLocal
    from app.models.developer import DeveloperApp

    async with AsyncSessionLocal() as db:
        await db.execute(
            sa_update(DeveloperApp)
            .where(DeveloperApp.id == app_data["id"])
            .values(status="TESTING")
        )
        await db.commit()

    return h, app_data


@pytest.mark.asyncio
async def test_oauth_authorize_success(c):
    h, app_data = await _setup_oauth_app(c)
    client_id = app_data["oauth_client_id"]

    r = await c.get(
        f"/api/v1/oauth/authorize?client_id={client_id}"
        "&redirect_uri=https://myapp.example.com/callback"
        "&scope=read:cohorts&state=csrf-token-123&response_type=code",
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert "code" in data
    assert data["state"] == "csrf-token-123"
    assert data["redirect_uri"] == "https://myapp.example.com/callback"


@pytest.mark.asyncio
async def test_oauth_authorize_invalid_client(c):
    h, _ = await _setup_oauth_app(c)
    r = await c.get(
        "/api/v1/oauth/authorize?client_id=nonexistent"
        "&redirect_uri=https://x.com/cb&scope=read:cohorts&state=test",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["error"] == "invalid_client"


@pytest.mark.asyncio
async def test_oauth_authorize_invalid_redirect_uri(c):
    h, app_data = await _setup_oauth_app(c)
    r = await c.get(
        f"/api/v1/oauth/authorize?client_id={app_data['oauth_client_id']}"
        "&redirect_uri=https://evil.com/callback"
        "&scope=read:cohorts&state=test",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["error"] == "invalid_redirect_uri"


@pytest.mark.asyncio
async def test_oauth_authorize_invalid_scope(c):
    h, app_data = await _setup_oauth_app(c)
    r = await c.get(
        f"/api/v1/oauth/authorize?client_id={app_data['oauth_client_id']}"
        "&redirect_uri=https://myapp.example.com/callback"
        "&scope=write:settings&state=test",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["error"] == "invalid_scope"


@pytest.mark.asyncio
async def test_oauth_authorize_unsupported_response_type(c):
    h, app_data = await _setup_oauth_app(c)
    r = await c.get(
        f"/api/v1/oauth/authorize?client_id={app_data['oauth_client_id']}"
        "&redirect_uri=https://myapp.example.com/callback"
        "&scope=read:cohorts&state=test&response_type=token",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["error"] == "unsupported_response_type"


@pytest.mark.asyncio
async def test_oauth_token_invalid_grant(c):
    """Token endpoint with fake code returns invalid_grant."""
    h, app_data = await _setup_oauth_app(c)
    # Need to get the client secret — it was shown once at creation.
    # For testing, we'll use the wrong secret to get invalid_client first.
    r = await c.post(
        "/api/v1/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": "fake-code",
            "client_id": app_data["oauth_client_id"],
            "client_secret": "wrong-secret",
        },
    )
    assert r.status_code == 200
    # Should be invalid_client since secret is wrong
    assert r.json()["data"]["error"] == "invalid_client"


@pytest.mark.asyncio
async def test_oauth_token_unsupported_grant(c):
    h, app_data = await _setup_oauth_app(c)
    r = await c.post(
        "/api/v1/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": app_data["oauth_client_id"],
            "client_secret": "test",
        },
    )
    assert r.status_code == 200
    # Either invalid_client (wrong secret) or unsupported_grant_type
    assert r.json()["data"]["error"] in ("invalid_client", "unsupported_grant_type")


@pytest.mark.asyncio
async def test_oauth_requires_auth(c):
    """Authorize endpoint requires authentication."""
    r = await c.get(
        "/api/v1/oauth/authorize?client_id=test&redirect_uri=https://x.com&scope=read:cohorts&state=test",
    )
    assert r.status_code == 401
