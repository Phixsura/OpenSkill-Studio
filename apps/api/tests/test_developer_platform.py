"""Integration tests for Developer Platform — accounts, apps, installations, keys, review."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"dev-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Dev"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


async def _dev_account(c, h, slug=None):
    slug = slug or f"dev-{uuid.uuid4().hex[:8]}"
    r = await c.post(
        "/api/v1/developer/accounts",
        json={
            "display_name": "Test Developer",
            "slug": slug,
            "support_email": f"{slug}@test.com",
        },
        headers=h,
    )
    assert r.status_code == 200, f"Dev account creation failed: {r.json()}"
    return r.json()["data"]


async def _dev_app(c, h, slug=None, category="connector"):
    slug = slug or f"app-{uuid.uuid4().hex[:8]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={
            "name": f"Test App {slug}",
            "slug": slug,
            "description": "A test application",
            "category": category,
        },
        headers=h,
    )
    assert r.status_code == 200, f"App creation failed: {r.json()}"
    return r.json()["data"]


# ── Developer Account Tests ──────────────────────────────


@pytest.mark.asyncio
async def test_create_developer_account(c):
    h, user = await _auth(c)
    account = await _dev_account(c, h)
    assert account["owner_user_id"] == user["id"]
    assert account["status"] == "active"
    assert account["verified"] is False


@pytest.mark.asyncio
async def test_get_my_developer_account(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    r = await c.get("/api/v1/developer/accounts/me", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["display_name"] == "Test Developer"


@pytest.mark.asyncio
async def test_duplicate_slug_rejected(c):
    h, _ = await _auth(c)
    slug = f"dup-{uuid.uuid4().hex[:8]}"
    await _dev_account(c, h, slug=slug)
    # Second account with same slug from different user
    h2, _ = await _auth(c)
    r = await c.post(
        "/api/v1/developer/accounts",
        json={
            "display_name": "Other Dev",
            "slug": slug,
            "support_email": "other@test.com",
        },
        headers=h2,
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_update_developer_account(c):
    h, _ = await _auth(c)
    account = await _dev_account(c, h)
    r = await c.patch(
        f"/api/v1/developer/accounts/{account['id']}",
        json={"display_name": "Updated Name"},
        headers=h,
    )
    assert r.status_code == 200, f"Update failed: {r.json()}"
    assert r.json()["data"]["display_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_list_developer_accounts(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    r = await c.get("/api/v1/developer/accounts", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1


# ── Developer App Tests ──────────────────────────────────


@pytest.mark.asyncio
async def test_create_app(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    assert app["status"] == "draft"
    assert app["category"] == "connector"
    assert app["oauth_client_id"] is not None
    assert app["oauth_client_id"].startswith("osk_")


@pytest.mark.asyncio
async def test_app_requires_developer_account(c):
    h, _ = await _auth(c)
    r = await c.post(
        "/api/v1/developer/apps",
        json={
            "name": "Test",
            "slug": "test-app",
            "category": "connector",
        },
        headers=h,
    )
    assert r.status_code == 404  # No developer account


@pytest.mark.asyncio
async def test_list_apps(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    await _dev_app(c, h)
    r = await c.get("/api/v1/developer/apps", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_get_app(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    r = await c.get(f"/api/v1/developer/apps/{app['id']}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["name"] == app["name"]


@pytest.mark.asyncio
async def test_update_app(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    r = await c.patch(
        f"/api/v1/developer/apps/{app['id']}",
        json={"description": "Updated description"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["description"] == "Updated description"


# ── App Version Tests ────────────────────────────────────


@pytest.mark.asyncio
async def test_create_app_version(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    r = await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {"name": "test"}, "permissions": []},
            "content_hash": "a" * 64,
        },
        headers=h,
    )
    assert r.status_code == 200
    v = r.json()["data"]
    assert v["version"] == "1.0.0"
    assert v["review_status"] == "pending"


@pytest.mark.asyncio
async def test_duplicate_version_rejected(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    version_data = {
        "version": "1.0.0",
        "manifest": {"schema_version": "1.0", "app": {"name": "test"}, "permissions": []},
        "content_hash": "b" * 64,
    }
    r1 = await c.post(f"/api/v1/developer/apps/{app['id']}/versions", json=version_data, headers=h)
    assert r1.status_code == 200
    r2 = await c.post(f"/api/v1/developer/apps/{app['id']}/versions", json=version_data, headers=h)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_list_app_versions(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "c" * 64,
        },
        headers=h,
    )
    r = await c.get(f"/api/v1/developer/apps/{app['id']}/versions", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1


# ── App Lifecycle Tests ──────────────────────────────────


@pytest.mark.asyncio
async def test_app_lifecycle_submit(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    # draft → testing
    r = await c.patch(
        f"/api/v1/developer/apps/{app['id']}",
        json={"visibility": "private"},
        headers=h,
    )
    assert r.status_code == 200

    # Need to be in testing state first
    # draft → testing (via transition)
    from app.models.developer import AppStatus

    # Submit directly from draft should fail (need testing first)
    r = await c.post(f"/api/v1/developer/apps/{app['id']}/submit", headers=h)
    # draft → submitted is not a valid transition
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_invalid_state_transition(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    # draft → published is not valid
    r = await c.post(f"/api/v1/developer/apps/{app['id']}/publish", headers=h)
    assert r.status_code == 422


# ── App Installation Tests ───────────────────────────────


@pytest.mark.asyncio
async def test_install_and_list(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    org_id = await _org(c, h)

    # Create a version first
    vr = await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "d" * 64,
        },
        headers=h,
    )
    version_id = vr.json()["data"]["id"]

    # Install
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app["id"], "app_version_id": version_id},
        headers=h,
    )
    assert r.status_code == 200
    inst = r.json()["data"]
    assert inst["status"] == "active"
    assert inst["org_id"] == org_id

    # List
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1


@pytest.mark.asyncio
async def test_duplicate_install_rejected(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    org_id = await _org(c, h)

    vr = await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "e" * 64,
        },
        headers=h,
    )
    version_id = vr.json()["data"]["id"]

    r1 = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app["id"], "app_version_id": version_id},
        headers=h,
    )
    assert r1.status_code == 200

    r2 = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app["id"], "app_version_id": version_id},
        headers=h,
    )
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_uninstall_app(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    org_id = await _org(c, h)

    vr = await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "f" * 64,
        },
        headers=h,
    )
    version_id = vr.json()["data"]["id"]

    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app["id"], "app_version_id": version_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]

    r = await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}", headers=h)
    assert r.status_code == 200


# ── API Key Tests ────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_and_list_api_keys(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)

    # Create key
    r = await c.post(
        f"/api/v1/developer/apps/{app['id']}/api-keys",
        json={"name": "Test Key", "scopes": ["read:cohorts"]},
        headers=h,
    )
    assert r.status_code == 200
    key_data = r.json()["data"]
    assert key_data["key"].startswith("osk_app_")
    assert key_data["key_prefix"] == key_data["key"][:12]

    # List keys
    r = await c.get(f"/api/v1/developer/apps/{app['id']}/api-keys", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
    # Listed key should NOT contain the full key
    assert "key" not in r.json()["data"][0] or r.json()["data"][0].get("key") is None


@pytest.mark.asyncio
async def test_revoke_api_key(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)

    r = await c.post(
        f"/api/v1/developer/apps/{app['id']}/api-keys",
        json={"name": "Revocable Key"},
        headers=h,
    )
    key_id = r.json()["data"]["id"]

    r = await c.delete(f"/api/v1/developer/apps/{app['id']}/api-keys/{key_id}", headers=h)
    assert r.status_code == 200


# ── Event Subscription Tests ─────────────────────────────


@pytest.mark.asyncio
async def test_event_subscriptions(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    org_id = await _org(c, h)

    vr = await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "1" * 64,
        },
        headers=h,
    )
    version_id = vr.json()["data"]["id"]

    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app["id"], "app_version_id": version_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]

    # Subscribe
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events",
        json={"event_type": "submission.completed"},
        headers=h,
    )
    assert r.status_code == 200
    sub = r.json()["data"]
    assert sub["event_type"] == "submission.completed"

    # List
    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events",
        headers=h,
    )
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1

    # Delete
    r = await c.delete(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events/{sub['id']}",
        headers=h,
    )
    assert r.status_code == 200


# ── Automation Rule Tests ────────────────────────────────


@pytest.mark.asyncio
async def test_automation_rules(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    org_id = await _org(c, h)

    vr = await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "2" * 64,
        },
        headers=h,
    )
    version_id = vr.json()["data"]["id"]

    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app["id"], "app_version_id": version_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]

    # Create rule
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules",
        json={
            "name": "Sync grades",
            "trigger_event": "submission.graded",
            "action_type": "webhook",
            "action_config": {"url": "https://example.com/hook", "method": "POST"},
        },
        headers=h,
    )
    assert r.status_code == 200
    rule = r.json()["data"]
    assert rule["name"] == "Sync grades"

    # List
    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules",
        headers=h,
    )
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1

    # Delete
    r = await c.delete(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules/{rule['id']}",
        headers=h,
    )
    assert r.status_code == 200


# ── Signing Key Tests ────────────────────────────────────


@pytest.mark.asyncio
async def test_signing_keys(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)

    # Register key
    r = await c.post(
        "/api/v1/developer/signing-keys",
        json={
            "name": "Production Key",
            "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI" + "A" * 44 + " test@dev",
        },
        headers=h,
    )
    assert r.status_code == 200
    key = r.json()["data"]
    assert key["name"] == "Production Key"
    assert len(key["fingerprint"]) == 16

    # List keys
    r = await c.get("/api/v1/developer/signing-keys", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1


# ── App Review Tests ─────────────────────────────────────


@pytest.mark.asyncio
async def test_submit_for_review(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)

    vr = await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {"name": "test"}, "permissions": ["read:cohorts"]},
            "content_hash": "3" * 64,
        },
        headers=h,
    )
    version_id = vr.json()["data"]["id"]

    r = await c.post(
        f"/api/v1/developer/apps/{app['id']}/reviews",
        json={"app_version_id": version_id},
        headers=h,
    )
    assert r.status_code == 200
    review = r.json()["data"]
    assert review["review_status"] == "pending"
    assert review["automated_checks"]["manifest_valid"] is True
    assert review["automated_checks"]["checks_passed"] is True


# ── Schema Validation Tests ──────────────────────────────


@pytest.mark.asyncio
async def test_invalid_slug_rejected(c):
    h, _ = await _auth(c)
    r = await c.post(
        "/api/v1/developer/accounts",
        json={
            "display_name": "Test",
            "slug": "INVALID SLUG!",
            "support_email": "test@test.com",
        },
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_invalid_category_rejected(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    r = await c.post(
        "/api/v1/developer/apps",
        json={
            "name": "Test",
            "slug": "test-app",
            "category": "invalid_category",
        },
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_invalid_version_format_rejected(c):
    h, _ = await _auth(c)
    await _dev_account(c, h)
    app = await _dev_app(c, h)
    r = await c.post(
        f"/api/v1/developer/apps/{app['id']}/versions",
        json={
            "version": "not-semver",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "4" * 64,
        },
        headers=h,
    )
    assert r.status_code == 422


# ── Marketplace Tests ────────────────────────────────────


@pytest.mark.asyncio
async def test_marketplace_browse_empty(c):
    """Marketplace browse works even with no published apps."""
    r = await c.get("/api/v1/marketplace/apps")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 0


@pytest.mark.asyncio
async def test_marketplace_app_not_found(c):
    """Non-existent app returns 404."""
    r = await c.get("/api/v1/marketplace/apps/nonexistent")
    assert r.status_code == 404
