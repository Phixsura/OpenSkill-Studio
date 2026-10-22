"""Tests for error handling across all developer platform endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"err-{uuid.uuid4().hex[:8]}@test.com"


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


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Err"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


# ── 404 responses ────────────────────────────────────────


@pytest.mark.asyncio
async def test_nonexistent_developer_account(c):
    h = await _auth(c)
    r = await c.get("/api/v1/developer/accounts/me", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_nonexistent_app_detail(c):
    h = await _auth(c)
    r = await c.get(f"/api/v1/developer/apps/{uuid.uuid4().hex[:26]}", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_nonexistent_marketplace_app(c):
    r = await c.get(f"/api/v1/marketplace/apps/{uuid.uuid4().hex[:26]}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_nonexistent_app_export(c):
    h = await _auth(c)
    r = await c.get(f"/api/v1/developer/apps/{uuid.uuid4().hex[:26]}/export", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_nonexistent_app_conformance(c):
    h = await _auth(c)
    r = await c.get(f"/api/v1/developer/apps/{uuid.uuid4().hex[:26]}/conformance", headers=h)
    assert r.status_code == 404


# ── 401 responses ────────────────────────────────────────


@pytest.mark.asyncio
async def test_no_auth_developer_accounts(c):
    r = await c.post("/api/v1/developer/accounts", json={"display_name": "X", "slug": "x", "support_email": "x@x.com"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_no_auth_create_app(c):
    r = await c.post("/api/v1/developer/apps", json={"name": "X", "slug": "x", "category": "connector"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_no_auth_signing_keys(c):
    r = await c.post("/api/v1/developer/signing-keys", json={"name": "X", "public_key": "X"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_no_auth_validate_manifest(c):
    r = await c.post("/api/v1/developer/validate-manifest", json={"manifest": {}})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_no_auth_tools(c):
    r = await c.post("/api/v1/developer/tools/send-test-event", json={"event_type": "test", "org_id": "x"})
    assert r.status_code == 401


# ── 422 validation errors ────────────────────────────────


@pytest.mark.asyncio
async def test_invalid_email_in_account(c):
    h = await _auth(c)
    r = await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "X", "slug": "valid-slug", "support_email": "not-an-email"},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_empty_app_name(c):
    h = await _auth(c)
    slug = f"emp-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "X", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "", "slug": "test", "category": "connector"},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_invalid_redirect_uri(c):
    h = await _auth(c)
    slug = f"rdr-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "X", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    r = await c.post(
        "/api/v1/developer/apps",
        json={
            "name": "Redirect App",
            "slug": f"rdrapp-{uuid.uuid4().hex[:4]}",
            "category": "connector",
            "redirect_uris": ["ftp://evil.com/callback"],
        },
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_invalid_automation_action_type(c):
    h = await _auth(c)
    slug = f"act-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Act Dev", "slug": slug, "support_email": f"{slug}@test.com"},
        headers=h,
    )
    assert r.status_code == 200, f"Dev account failed: {r.json()}"
    app_slug = f"actapp-{uuid.uuid4().hex[:4]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Act App", "slug": app_slug, "category": "connector"},
        headers=h,
    )
    assert r.status_code == 200, f"App creation failed: {r.json()}"
    app_id = r.json()["data"]["id"]
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "a" * 64,
        },
        headers=h,
    )
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]

    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules",
        json={
            "name": "Bad rule",
            "trigger_event": "submission.completed",
            "action_type": "invalid_type",
            "action_config": {},
        },
        headers=h,
    )
    assert r.status_code == 422
