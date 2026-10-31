"""Advanced OAuth flow tests."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"oa-{uuid.uuid4().hex[:8]}@test.com"


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
async def test_oauth_token_missing_code(c):
    r = await c.post("/api/v1/oauth/token", data={
        "grant_type": "authorization_code", "client_id": "osk_fake", "client_secret": "wrong",
    })
    assert r.status_code == 200
    assert r.json()["data"]["error"] == "invalid_client"


@pytest.mark.asyncio
async def test_oauth_token_no_grant_type_match(c):
    r = await c.post("/api/v1/oauth/token", data={
        "grant_type": "password", "client_id": "osk_fake", "client_secret": "wrong",
    })
    assert r.status_code == 200
    assert r.json()["data"]["error"] in ("invalid_client", "unsupported_grant_type")


@pytest.mark.asyncio
async def test_authorize_without_auth(c):
    r = await c.get("/api/v1/oauth/authorize?client_id=x&redirect_uri=https://x.com&scope=read:cohorts&state=test")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_authorize_bad_response_type(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "OA"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get("/api/v1/oauth/authorize?client_id=osk_test&redirect_uri=https://x.com&scope=read:cohorts&state=t&response_type=implicit", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["error"] == "unsupported_response_type"


@pytest.mark.asyncio
async def test_token_endpoint_accepts_form_data(c):
    """Token endpoint uses Form, not Query."""
    r = await c.post("/api/v1/oauth/token", data={
        "grant_type": "authorization_code", "code": "fake",
        "client_id": "osk_test", "client_secret": "test_secret",
    })
    assert r.status_code == 200
    # Should get invalid_client (not a 422 validation error)
    assert "error" in r.json()["data"]
