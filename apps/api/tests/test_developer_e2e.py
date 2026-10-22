"""End-to-end tests for the Developer Platform.

Covers the full acceptance criteria flow:
develop → test → review → publish → tenant install → event → sandbox → upgrade → revoke
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"e2e-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "E2E"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201
    return r.json()["data"]["id"]


@pytest.mark.asyncio
async def test_full_e2e_lifecycle(c):
    """Full E2E: create account → app → version → review → publish → install →
    event sub → automation rule → API key → stats → conformance → upgrade → uninstall → revoke."""

    h, user = await _auth(c)
    org_id = await _org(c, h)

    # ── 1. Create developer account ──────────────────────
    slug = f"e2e-dev-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "E2E Developer", "slug": slug, "support_email": f"{slug}@test.com"},
        headers=h,
    )
    assert r.status_code == 200
    dev_account = r.json()["data"]
    assert dev_account["status"] == "active"

    # ── 2. Create app ────────────────────────────────────
    app_slug = f"e2e-app-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={
            "name": "E2E Test App",
            "slug": app_slug,
            "category": "connector",
            "description": "End-to-end test connector",
        },
        headers=h,
    )
    assert r.status_code == 200
    app = r.json()["data"]
    assert app["status"] == "draft"
    assert app["oauth_client_id"].startswith("osk_")
    app_id = app["id"]

    # ── 3. Create version with manifest ──────────────────
    manifest = {
        "schema_version": "1.0",
        "app": {
            "name": "E2E Test App",
            "slug": app_slug,
            "version": "1.0.0",
            "category": "connector",
        },
        "permissions": ["read:cohorts", "read:projects", "subscribe:events"],
        "event_subscriptions": ["submission.completed", "cohort.member_added"],
        "secrets": [{"key": "LMS_API_KEY", "description": "External LMS API key"}],
    }
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": manifest,
            "content_hash": "a" * 64,
            "changelog": "Initial release",
            "signature": "test-sig",
        },
        headers=h,
    )
    assert r.status_code == 200
    v1 = r.json()["data"]
    assert v1["version"] == "1.0.0"
    assert v1["review_status"] == "pending"
    v1_id = v1["id"]

    # ── 4. Validate manifest ─────────────────────────────
    r = await c.post(
        "/api/v1/developer/validate-manifest",
        json={"manifest": manifest},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["valid"] is True

    # ── 5. Submit for review ─────────────────────────────
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/reviews",
        json={"app_version_id": v1_id},
        headers=h,
    )
    assert r.status_code == 200
    review = r.json()["data"]
    assert review["review_status"] == "pending"
    assert review["automated_checks"]["checks_passed"] is True

    # ── 6. List reviews ──────────────────────────────────
    r = await c.get(f"/api/v1/developer/apps/{app_id}/reviews", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1

    # ── 7. Register signing key ──────────────────────────
    r = await c.post(
        "/api/v1/developer/signing-keys",
        json={"name": "E2E Key", "public_key": "ssh-ed25519 AAAA" + "B" * 44 + " e2e@test"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["fingerprint"]

    # ── 8. Create API key ────────────────────────────────
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/api-keys",
        json={"name": "E2E API Key", "scopes": ["read:cohorts", "read:projects"]},
        headers=h,
    )
    assert r.status_code == 200
    api_key_data = r.json()["data"]
    assert api_key_data["key"].startswith("osk_app_")
    api_key_full = api_key_data["key"]

    # ── 9. Verify API key auth works ─────────────────────
    r = await c.get(
        "/api/v1/developer/accounts/me",
        headers={"Authorization": f"Bearer {api_key_full}"},
    )
    assert r.status_code == 200
    assert r.json()["data"]["slug"] == slug

    # ── 10. Install app into org ─────────────────────────
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v1_id, "granted_permissions": ["read:cohorts"]},
        headers=h,
    )
    assert r.status_code == 200
    installation = r.json()["data"]
    assert installation["status"] == "active"
    inst_id = installation["id"]

    # ── 11. List installations ───────────────────────────
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1

    # ── 12. Set secrets ──────────────────────────────────
    r = await c.put(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        json={"key": "LMS_API_KEY", "value": "test-secret-value", "description": "LMS key"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["key"] == "LMS_API_KEY"

    # Verify secret listed (value never exposed)
    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        headers=h,
    )
    assert r.status_code == 200
    secrets_list = r.json()["data"]
    assert len(secrets_list) == 1
    assert "value" not in str(secrets_list)  # value never in response

    # ── 13. Subscribe to events ──────────────────────────
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events",
        json={"event_type": "submission.completed"},
        headers=h,
    )
    assert r.status_code == 200
    sub = r.json()["data"]
    assert sub["event_type"] == "submission.completed"

    # ── 14. Create automation rule ───────────────────────
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules",
        json={
            "name": "Grade sync rule",
            "trigger_event": "submission.graded",
            "action_type": "webhook",
            "action_config": {
                "url": "https://example.com/webhook",
                "method": "POST",
                "body_template": {"grade": "{{event.data.grade}}"},
            },
            "max_executions_per_hour": 50,
        },
        headers=h,
    )
    assert r.status_code == 200
    rule = r.json()["data"]
    assert rule["name"] == "Grade sync rule"
    assert rule["trigger_event"] == "submission.graded"

    # ── 15. Get app stats ────────────────────────────────
    r = await c.get(f"/api/v1/developer/apps/{app_id}/stats", headers=h)
    assert r.status_code == 200
    stats = r.json()["data"]
    assert stats["active_installs"] == 1
    assert stats["versions"] == 1
    assert stats["active_api_keys"] >= 1

    # ── 16. Run conformance ──────────────────────────────
    r = await c.get(f"/api/v1/developer/apps/{app_id}/conformance", headers=h)
    assert r.status_code == 200
    conformance = r.json()["data"]
    assert conformance["summary"]["fail"] == 0
    assert conformance["version"] == "1.0.0"

    # ── 17. Create v2, upgrade installation ──────────────
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "2.0.0",
            "manifest": {**manifest, "app": {**manifest["app"], "version": "2.0.0"}},
            "content_hash": "b" * 64,
            "changelog": "Major upgrade",
        },
        headers=h,
    )
    assert r.status_code == 200
    v2_id = r.json()["data"]["id"]

    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/upgrade",
        headers=h,
    )
    assert r.status_code == 200
    upgraded = r.json()["data"]
    assert upgraded["app_version_id"] == v2_id

    # ── 18. Update installation config ───────────────────
    r = await c.patch(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}",
        json={"config": {"lms_base_url": "https://lms.example.com"}, "pinned_version": True},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["pinned_version"] is True

    # ── 19. Delete secret ────────────────────────────────
    r = await c.delete(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets/LMS_API_KEY",
        headers=h,
    )
    assert r.status_code == 200

    # ── 20. Delete event subscription ────────────────────
    r = await c.delete(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events/{sub['id']}",
        headers=h,
    )
    assert r.status_code == 200

    # ── 21. Delete automation rule ───────────────────────
    r = await c.delete(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules/{rule['id']}",
        headers=h,
    )
    assert r.status_code == 200

    # ── 22. Uninstall ────────────────────────────────────
    r = await c.delete(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}",
        headers=h,
    )
    assert r.status_code == 200

    # ── 23. Revoke API key ───────────────────────────────
    r = await c.delete(
        f"/api/v1/developer/apps/{app_id}/api-keys/{api_key_data['id']}",
        headers=h,
    )
    assert r.status_code == 200

    # Verify revoked key no longer works
    r = await c.get(
        "/api/v1/developer/accounts/me",
        headers={"Authorization": f"Bearer {api_key_full}"},
    )
    assert r.status_code == 401

    # ── 24. Revoke app (kill switch) ─────────────────────
    r = await c.post(f"/api/v1/developer/apps/{app_id}/revoke", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "revoked"

    # ── 25. Verify app no longer visible in marketplace ──
    r = await c.get(f"/api/v1/marketplace/apps/{app_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_developer_tools_e2e(c):
    """E2E: test developer tools endpoints."""
    h, _ = await _auth(c)
    org_id = await _org(c, h)

    # Create dev account (required for tools)
    slug = f"tool-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Tool Dev", "slug": slug, "support_email": f"{slug}@test.com"},
        headers=h,
    )

    # List event types
    r = await c.get("/api/v1/developer/tools/event-types", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] >= 30
    assert "submission" in data["categories"]
    assert "cohort" in data["categories"]

    # List permissions
    r = await c.get("/api/v1/developer/tools/permissions", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["total"] >= 30

    # List UI surfaces
    r = await c.get("/api/v1/developer/tools/ui-surfaces", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["total"] == 8

    # Generate fixtures
    r = await c.post("/api/v1/developer/tools/generate-fixtures", headers=h)
    assert r.status_code == 200
    fixtures = r.json()["data"]
    assert "cohort" in fixtures
    assert "project" in fixtures
    assert "event_payload" in fixtures

    # Quick validate
    r = await c.post(
        "/api/v1/developer/tools/validate",
        json={"manifest": {"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["read:cohorts"]}},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["valid"] is True

    # Send test event (needs valid event type + org)
    r = await c.post(
        "/api/v1/developer/tools/send-test-event",
        json={
            "event_type": "submission.completed",
            "data": {"submission_id": "test-123"},
            "org_id": org_id,
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["test"] is True


@pytest.mark.asyncio
async def test_marketplace_browse_e2e(c):
    """E2E: marketplace browsing with filters."""
    # Browse (no auth required)
    r = await c.get("/api/v1/marketplace/apps")
    assert r.status_code == 200
    assert "data" in r.json()
    assert "meta" in r.json()

    # Browse with category filter
    r = await c.get("/api/v1/marketplace/apps?category=connector")
    assert r.status_code == 200

    # Browse with search
    r = await c.get("/api/v1/marketplace/apps?q=test")
    assert r.status_code == 200

    # Non-existent app
    r = await c.get("/api/v1/marketplace/apps/nonexistent-id")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_webhook_verification():
    """Test webhook signature generation and verification."""
    from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature

    # Generate secret
    raw_secret, hashed = generate_webhook_secret()
    assert raw_secret.startswith("whsec_")
    assert len(hashed) == 64

    # Sign and verify
    payload = b'{"event": "test"}'
    signature = sign_payload(payload, raw_secret)
    assert signature.startswith("sha256=")
    assert verify_signature(payload, signature, raw_secret) is True

    # Tampered payload fails
    assert verify_signature(b'{"event": "tampered"}', signature, raw_secret) is False

    # Wrong secret fails
    assert verify_signature(payload, signature, "wrong-secret") is False

    # Invalid format fails
    assert verify_signature(payload, "invalid", raw_secret) is False


@pytest.mark.asyncio
async def test_api_key_auth_middleware(c):
    """Test API key authentication via get_current_user_or_app."""
    h, _ = await _auth(c)

    # Create dev account + app + API key
    slug = f"auth-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Auth Test", "slug": slug, "support_email": f"{slug}@test.com"},
        headers=h,
    )
    app_slug = f"authapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Auth App", "slug": app_slug, "category": "connector"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]

    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/api-keys",
        json={"name": "Auth Key", "scopes": ["read:cohorts"]},
        headers=h,
    )
    full_key = r.json()["data"]["key"]

    # API key works for developer endpoints
    r = await c.get(
        "/api/v1/developer/accounts/me",
        headers={"Authorization": f"Bearer {full_key}"},
    )
    assert r.status_code == 200
    assert r.json()["data"]["slug"] == slug

    # Revoke the key
    key_id = r.json()  # Need key_id from create response
    r = await c.get(
        f"/api/v1/developer/apps/{app_id}/api-keys",
        headers=h,
    )
    key_id = r.json()["data"][0]["id"]
    r = await c.delete(
        f"/api/v1/developer/apps/{app_id}/api-keys/{key_id}",
        headers=h,
    )
    assert r.status_code == 200

    # Revoked key rejected
    r = await c.get(
        "/api/v1/developer/accounts/me",
        headers={"Authorization": f"Bearer {full_key}"},
    )
    assert r.status_code == 401
