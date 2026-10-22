"""Integration tests verifying SDK type contracts match the API."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"sdk-{uuid.uuid4().hex[:8]}@test.com"


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
async def test_developer_account_response_shape(c):
    """API response matches SDK DeveloperAccountResponse type."""
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "SDK"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"sdk-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/accounts", json={
        "display_name": "SDK Dev", "slug": slug, "support_email": f"{slug}@t.com",
    }, headers=h)
    data = r.json()["data"]
    # Verify all SDK-expected fields exist
    for field in ["id", "owner_user_id", "display_name", "slug", "support_email", "verified", "status", "created_at", "updated_at"]:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_app_response_shape(c):
    """API response matches SDK AppResponse type."""
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "SDK"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"sdka-{uuid.uuid4().hex[:6]}"
    r2 = await c.post("/api/v1/developer/accounts", json={"display_name": "SDK Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    assert r2.status_code == 200, f"Dev account failed: {r2.json()}"
    r = await c.post("/api/v1/developer/apps", json={"name": "SDK App", "slug": f"sdkapp-{uuid.uuid4().hex[:4]}", "category": "connector"}, headers=h)
    data = r.json()["data"]
    for field in ["id", "developer_id", "name", "slug", "category", "visibility", "status", "oauth_client_id", "created_at", "updated_at"]:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_version_response_shape(c):
    """API response matches SDK AppVersionResponse type."""
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "SDK"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"sdkv-{uuid.uuid4().hex[:6]}"
    r2 = await c.post("/api/v1/developer/accounts", json={"display_name": "SDK Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    assert r2.status_code == 200, f"Dev account failed: {r2.json()}"
    r = await c.post("/api/v1/developer/apps", json={"name": "V App", "slug": f"vapp-{uuid.uuid4().hex[:4]}", "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "a" * 64,
    }, headers=h)
    data = r.json()["data"]
    for field in ["id", "app_id", "version", "content_hash", "review_status", "created_at"]:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_installation_response_shape(c):
    """API response matches SDK AppInstallationResponse type."""
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "SDK"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"sdki-{uuid.uuid4().hex[:6]}"
    r2 = await c.post("/api/v1/developer/accounts", json={"display_name": "SDK Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    assert r2.status_code == 200, f"Dev account failed: {r2.json()}"
    r = await c.post("/api/v1/developer/apps", json={"name": "I App", "slug": f"iapp-{uuid.uuid4().hex[:4]}", "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "b" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v_id}, headers=h)
    data = r.json()["data"]
    for field in ["id", "app_id", "app_version_id", "org_id", "installed_by", "status", "granted_permissions", "config", "pinned_version", "created_at", "updated_at"]:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_api_key_response_shape(c):
    """API response matches SDK ApiKeyCreatedResponse type."""
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "SDK"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"sdkk-{uuid.uuid4().hex[:6]}"
    r2 = await c.post("/api/v1/developer/accounts", json={"display_name": "SDK Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    assert r2.status_code == 200, f"Dev account failed: {r2.json()}"
    r = await c.post("/api/v1/developer/apps", json={"name": "K App", "slug": f"kapp-{uuid.uuid4().hex[:4]}", "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/api-keys", json={"name": "SDK Key"}, headers=h)
    data = r.json()["data"]
    for field in ["id", "key", "key_prefix", "name", "scopes"]:
        assert field in data, f"Missing field: {field}"
    assert data["key"].startswith("osk_app_")


@pytest.mark.asyncio
async def test_data_response_wrapper(c):
    """All responses use {data: T} wrapper."""
    r = await c.get("/api/v1/marketplace/apps")
    assert "data" in r.json()
    assert "meta" in r.json()

    r = await c.get("/api/v1/marketplace/categories")
    assert "data" in r.json()

    r = await c.get("/api/v1/marketplace/featured")
    assert "data" in r.json()


@pytest.mark.asyncio
async def test_list_response_wrapper(c):
    """List responses use {data: T[], meta: {total, page, per_page, has_more}}."""
    r = await c.get("/api/v1/marketplace/apps")
    meta = r.json()["meta"]
    for field in ["total", "page", "per_page", "has_more"]:
        assert field in meta, f"Missing meta field: {field}"


@pytest.mark.asyncio
async def test_error_response_wrapper(c):
    """Error responses use {error: {code, message}}."""
    r = await c.get("/api/v1/marketplace/apps/nonexistent")
    assert r.status_code == 404
    err = r.json()["error"]
    assert "code" in err
    assert "message" in err
