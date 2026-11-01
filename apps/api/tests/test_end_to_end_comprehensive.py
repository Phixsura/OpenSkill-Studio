"""Comprehensive end-to-end test covering the full developer platform flow.

Single test that walks through every major feature in sequence.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"full-{uuid.uuid4().hex[:8]}@test.com"


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
async def test_complete_developer_platform_flow(c):
    """Single comprehensive test covering every major platform feature."""

    # ── 1. Register user ─────────────────────────────────
    h1_r = await c.post("/api/v1/auth/register", json={
        "email": _email(), "password": "TestPass123!", "display_name": "Full E2E",
    })
    h = {"Authorization": f"Bearer {h1_r.json()['access_token']}"}

    # ── 2. Create developer account ──────────────────────
    slug = f"full-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/accounts", json={
        "display_name": "Full E2E Dev", "slug": slug, "support_email": f"{slug}@t.com",
    }, headers=h)
    assert r.status_code == 200
    dev_id = r.json()["data"]["id"]

    # Read back
    r = await c.get("/api/v1/developer/accounts/me", headers=h)
    assert r.json()["data"]["slug"] == slug

    # ── 3. Create app ────────────────────────────────────
    app_slug = f"fapp-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={
        "name": "Full E2E App", "slug": app_slug, "category": "connector",
        "description": "Comprehensive test app",
        "redirect_uris": ["https://example.com/cb"],
    }, headers=h)
    assert r.status_code == 200
    app_data = r.json()["data"]
    app_id = app_data["id"]
    assert app_data["oauth_client_id"].startswith("osk_")

    # ── 4. Create version ────────────────────────────────
    manifest = {
        "schema_version": "1.0",
        "app": {"name": "Full E2E", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "read:projects", "subscribe:events"],
        "event_subscriptions": ["submission.completed"],
        "secrets": [{"key": "LMS_KEY", "description": "LMS API key"}],
    }
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": manifest, "content_hash": "a" * 64,
        "changelog": "Initial", "signature": "ed25519-sig",
    }, headers=h)
    assert r.status_code == 200
    v1_id = r.json()["data"]["id"]

    # ── 5. Validate manifest ─────────────────────────────
    r = await c.post("/api/v1/developer/validate-manifest", json={"manifest": manifest}, headers=h)
    assert r.json()["data"]["valid"] is True

    # ── 6. Register signing key ──────────────────────────
    r = await c.post("/api/v1/developer/signing-keys", json={
        "name": "E2E Key", "public_key": "ssh-ed25519 AAAA" + "X" * 44 + " e2e",
    }, headers=h)
    assert r.status_code == 200

    # ── 7. Create API key ────────────────────────────────
    r = await c.post(f"/api/v1/developer/apps/{app_id}/api-keys", json={
        "name": "E2E Key", "scopes": ["read:cohorts"],
    }, headers=h)
    assert r.status_code == 200
    api_key = r.json()["data"]["key"]
    key_id = r.json()["data"]["id"]

    # Verify API key auth
    r = await c.get("/api/v1/developer/accounts/me", headers={"Authorization": f"Bearer {api_key}"})
    assert r.status_code == 200

    # ── 8. Create org + install ──────────────────────────
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]

    r = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={
        "app_id": app_id, "app_version_id": v1_id,
        "granted_permissions": ["read:cohorts"],
    }, headers=h)
    assert r.status_code == 200
    inst_id = r.json()["data"]["id"]

    # ── 9. Configure installation ────────────────────────
    r = await c.patch(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}", json={
        "config": {"lms_url": "https://lms.test"}, "pinned_version": False,
    }, headers=h)
    assert r.status_code == 200

    # ── 10. Set secret ───────────────────────────────────
    r = await c.put(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", json={
        "key": "LMS_KEY", "value": "secret-123", "description": "API key",
    }, headers=h)
    assert r.status_code == 200

    # ── 11. Subscribe to event ───────────────────────────
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events", json={
        "event_type": "submission.completed",
    }, headers=h)
    assert r.status_code == 200
    sub_id = r.json()["data"]["id"]

    # ── 12. Create automation rule ───────────────────────
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules", json={
        "name": "Grade sync", "trigger_event": "submission.graded",
        "action_type": "webhook", "action_config": {"url": "https://lms.test/sync"},
    }, headers=h)
    assert r.status_code == 200
    rule_id = r.json()["data"]["id"]

    # ── 13. Execute sandbox ──────────────────────────────
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute", json={
        "function_name": "on_submission", "payload": {"grade": 85},
    }, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["success"] is True

    # ── 14. Check stats + conformance ────────────────────
    r = await c.get(f"/api/v1/developer/apps/{app_id}/stats", headers=h)
    assert r.json()["data"]["active_installs"] == 1

    r = await c.get(f"/api/v1/developer/apps/{app_id}/conformance", headers=h)
    assert r.json()["data"]["summary"]["fail"] == 0

    r = await c.get(f"/api/v1/developer/apps/{app_id}/health", headers=h)
    assert r.status_code == 200

    r = await c.get(f"/api/v1/developer/apps/{app_id}/analytics/summary", headers=h)
    assert r.json()["data"]["active_installs"] == 1

    # ── 15. Export ────────────────────────────────────────
    r = await c.get(f"/api/v1/developer/apps/{app_id}/export", headers=h)
    assert r.json()["data"]["version_count"] == 1

    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/export", headers=h)
    assert len(r.json()["data"]["event_subscriptions"]) == 1

    # ── 16. Version upgrade ──────────────────────────────
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "2.0.0", "manifest": {**manifest, "app": {**manifest["app"], "version": "2.0.0"}},
        "content_hash": "b" * 64, "changelog": "Version 2",
    }, headers=h)
    v2_id = r.json()["data"]["id"]

    # Compatibility check
    r = await c.post(f"/api/v1/developer/apps/{app_id}/check-compatibility", json={
        "current_version_id": v1_id, "new_version_id": v2_id,
    }, headers=h)
    assert r.json()["data"]["compatible"] is True

    # Upgrade
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/upgrade", headers=h)
    assert r.json()["data"]["app_version_id"] == v2_id

    # Pin
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/pin", headers=h)
    assert r.json()["data"]["pinned_version"] is True

    # Rollback
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rollback", json={
        "target_version_id": v1_id,
    }, headers=h)
    assert r.json()["data"]["app_version_id"] == v1_id

    # ── 17. Cleanup ──────────────────────────────────────
    await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events/{sub_id}", headers=h)
    await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules/{rule_id}", headers=h)
    await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets/LMS_KEY", headers=h)
    await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}", headers=h)

    # Revoke API key
    await c.delete(f"/api/v1/developer/apps/{app_id}/api-keys/{key_id}", headers=h)
    r = await c.get("/api/v1/developer/accounts/me", headers={"Authorization": f"Bearer {api_key}"})
    assert r.status_code == 401

    # Revoke app
    r = await c.post(f"/api/v1/developer/apps/{app_id}/revoke", headers=h)
    assert r.json()["data"]["status"] == "revoked"

    # Verify not in marketplace
    r = await c.get(f"/api/v1/marketplace/apps/{app_id}")
    assert r.status_code == 404

    # ── 18. Marketplace browsing (public) ────────────────
    assert (await c.get("/api/v1/marketplace/apps")).status_code == 200
    assert (await c.get("/api/v1/marketplace/categories")).status_code == 200
    assert (await c.get("/api/v1/marketplace/featured")).status_code == 200
    assert (await c.get("/api/v1/marketplace/recent")).status_code == 200
    assert (await c.get("/api/v1/marketplace/trending")).status_code == 200

    # ── 19. Developer tools ──────────────────────────────
    assert (await c.get("/api/v1/developer/tools/event-types", headers=h)).status_code == 200
    assert (await c.get("/api/v1/developer/tools/permissions", headers=h)).status_code == 200
    assert (await c.get("/api/v1/developer/tools/ui-surfaces", headers=h)).status_code == 200
    assert (await c.post("/api/v1/developer/tools/generate-fixtures", headers=h)).status_code == 200
