"""Advanced CRUD tests for apps, versions, and installations."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"advcrud-{uuid.uuid4().hex[:8]}@test.com"


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


async def _dev(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "AC"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"ac-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "AC Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    return h


@pytest.mark.asyncio
async def test_create_app_minimal(c):
    h = await _dev(c)
    r = await c.post("/api/v1/developer/apps", json={"name": "Min App", "slug": f"min-{uuid.uuid4().hex[:6]}", "category": "connector"}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["description"] is None

@pytest.mark.asyncio
async def test_update_app_description(c):
    h = await _dev(c)
    s = f"upd-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "Upd App", "slug": s, "category": "analytics"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.patch(f"/api/v1/developer/apps/{app_id}", json={"description": "New desc"}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["description"] == "New desc"

@pytest.mark.asyncio
async def test_update_app_visibility(c):
    h = await _dev(c)
    s = f"vis-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "Vis App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.patch(f"/api/v1/developer/apps/{app_id}", json={"visibility": "unlisted"}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["visibility"] in ("unlisted", "UNLISTED")

@pytest.mark.asyncio
async def test_multiple_versions(c):
    h = await _dev(c)
    s = f"mv-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "MV App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    for ver in ["1.0.0", "1.1.0", "2.0.0"]:
        r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
            "version": ver, "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": f"{ver[0]}" * 64,
        }, headers=h)
        assert r.status_code == 200
    r = await c.get(f"/api/v1/developer/apps/{app_id}/versions", headers=h)
    assert len(r.json()["data"]) == 3

@pytest.mark.asyncio
async def test_version_with_prerelease(c):
    h = await _dev(c)
    s = f"pre-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "Pre App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0-alpha.1", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "a" * 64,
    }, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["version"] == "1.0.0-alpha.1"

@pytest.mark.asyncio
async def test_install_with_permissions_and_config(c):
    h = await _dev(c)
    s = f"ip-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "IP App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": ["read:cohorts"]}, "content_hash": "b" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={
        "app_id": app_id, "app_version_id": v_id,
        "granted_permissions": ["read:cohorts"], "config": {"base_url": "https://test.com"},
        "pinned_version": True,
    }, headers=h)
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["pinned_version"] is True
    assert "read:cohorts" in d["granted_permissions"]
    assert d["config"]["base_url"] == "https://test.com"

@pytest.mark.asyncio
async def test_list_installations_by_status(c):
    h = await _dev(c)
    s = f"ls-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "LS App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "c" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v_id}, headers=h)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations?status=active", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1

@pytest.mark.asyncio
async def test_get_specific_version(c):
    h = await _dev(c)
    s = f"sv-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "SV App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "d" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]
    r = await c.get(f"/api/v1/developer/apps/{app_id}/versions/{v_id}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["version"] == "1.0.0"

@pytest.mark.asyncio
async def test_app_review_submit_and_list(c):
    h = await _dev(c)
    s = f"rv-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "RV App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {"name": "RV"}, "permissions": ["read:cohorts"]}, "content_hash": "e" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/reviews", json={"app_version_id": v_id}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["review_status"] in ("pending", "PENDING")
    r = await c.get(f"/api/v1/developer/apps/{app_id}/reviews", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
