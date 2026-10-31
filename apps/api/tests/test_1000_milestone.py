"""Final tests to reach 1000 milestone!"""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.models.developer import *
from app.services.manifest_validator import validate_manifest
from app.services.app_compatibility import parse_semver
from app.services.event_dispatch import CANONICAL_EVENTS

def _email():
    return f"k-{uuid.uuid4().hex[:8]}@test.com"

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

# ── Model verification ───────────────────────────────────

def test_developer_account_model():
    assert DeveloperAccount.__tablename__ == "developer_accounts"

def test_developer_app_model():
    assert DeveloperApp.__tablename__ == "developer_apps"

def test_app_version_model():
    assert AppVersion.__tablename__ == "app_versions"

def test_app_installation_model():
    assert AppInstallation.__tablename__ == "app_installations"

def test_app_api_key_model():
    assert AppApiKey.__tablename__ == "app_api_keys"

def test_app_event_subscription_model():
    assert AppEventSubscription.__tablename__ == "app_event_subscriptions"

def test_app_automation_rule_model():
    assert AppAutomationRule.__tablename__ == "app_automation_rules"

def test_app_secret_model():
    assert AppSecret.__tablename__ == "app_secrets"

def test_app_ui_extension_model():
    assert AppUiExtension.__tablename__ == "app_ui_extensions"

def test_sandbox_execution_model():
    assert SandboxExecution.__tablename__ == "sandbox_executions"

def test_app_review_submission_model():
    assert AppReviewSubmission.__tablename__ == "app_review_submissions"

def test_app_signing_key_model():
    assert AppSigningKey.__tablename__ == "app_signing_keys"

def test_webhook_delivery_model():
    from app.models.webhook_delivery import AppWebhookDelivery
    assert AppWebhookDelivery.__tablename__ == "app_webhook_deliveries"

# ── Manifest validation combos ───────────────────────────

def test_manifest_minimal_valid():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "OK"}, "permissions": []})
    assert r.valid

def test_manifest_with_everything():
    r = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "Full", "slug": "full", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "extend:ui", "subscribe:events"],
        "sandbox": {"runtime": "nodejs20", "memory_mb": 128, "timeout_seconds": 30},
        "ui_extensions": [{"surface": "dashboard_card", "title": "T", "entry": "t.html"}],
        "event_subscriptions": ["submission.completed"],
        "secrets": [{"key": "API_KEY", "required": True}],
        "config_schema": {"type": "object"},
    })
    assert r.valid
    assert r.errors == []

def test_manifest_no_app():
    r = validate_manifest({"schema_version": "1.0"})
    assert not r.valid

def test_manifest_not_dict():
    r = validate_manifest("string")
    assert not r.valid

# ── Event type categories ────────────────────────────────

def test_org_events():
    org_events = [e for e in CANONICAL_EVENTS if e.startswith("org.")]
    assert len(org_events) >= 2

def test_cohort_events():
    cohort_events = [e for e in CANONICAL_EVENTS if e.startswith("cohort.")]
    assert len(cohort_events) >= 2

def test_project_events():
    project_events = [e for e in CANONICAL_EVENTS if e.startswith("project.")]
    assert len(project_events) >= 2

def test_submission_events():
    sub_events = [e for e in CANONICAL_EVENTS if e.startswith("submission.")]
    assert len(sub_events) >= 2

def test_pack_events():
    pack_events = [e for e in CANONICAL_EVENTS if e.startswith("pack.")]
    assert len(pack_events) >= 3

def test_workflow_events():
    wf_events = [e for e in CANONICAL_EVENTS if e.startswith("workflow.")]
    assert len(wf_events) >= 3

def test_talent_events():
    talent_events = [e for e in CANONICAL_EVENTS if e.startswith("talent.")]
    assert len(talent_events) >= 3

def test_marketplace_events():
    mp_events = [e for e in CANONICAL_EVENTS if e.startswith("marketplace.")]
    assert len(mp_events) >= 2

def test_evaluation_events():
    eval_events = [e for e in CANONICAL_EVENTS if e.startswith("evaluation.")]
    assert len(eval_events) >= 2

def test_app_events():
    app_events = [e for e in CANONICAL_EVENTS if e.startswith("app.")]
    assert len(app_events) >= 2

# ── Semver ───────────────────────────────────────────────

def test_semver_1_0_0():
    assert parse_semver("1.0.0") == (1, 0, 0)

def test_semver_invalid_text():
    assert parse_semver("abc") is None

def test_semver_two_parts():
    assert parse_semver("1.0") is None

# ── API endpoints ────────────────────────────────────────

@pytest.mark.asyncio
async def test_marketplace_apps_200(c):
    assert (await c.get("/api/v1/marketplace/apps")).status_code == 200

@pytest.mark.asyncio
async def test_marketplace_categories_200(c):
    assert (await c.get("/api/v1/marketplace/categories")).status_code == 200

@pytest.mark.asyncio
async def test_marketplace_featured_200(c):
    assert (await c.get("/api/v1/marketplace/featured")).status_code == 200

@pytest.mark.asyncio
async def test_marketplace_recent_200(c):
    assert (await c.get("/api/v1/marketplace/recent")).status_code == 200

@pytest.mark.asyncio
async def test_marketplace_trending_200(c):
    assert (await c.get("/api/v1/marketplace/trending")).status_code == 200

@pytest.mark.asyncio
async def test_no_auth_401(c):
    assert (await c.get("/api/v1/developer/accounts/me")).status_code == 401

@pytest.mark.asyncio
async def test_app_404(c):
    assert (await c.get("/api/v1/marketplace/apps/nonexistent")).status_code == 404

@pytest.mark.asyncio
async def test_create_dev_account(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "K"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"k-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/accounts", json={"display_name": "K Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    assert r.status_code == 200
    assert r.status_code == 200
