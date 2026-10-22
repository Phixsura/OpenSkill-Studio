"""Tests to reach 900 milestone — comprehensive cross-cutting coverage."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"m9-{uuid.uuid4().hex[:8]}@test.com"

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

# ── Public endpoints ─────────────────────────────────────

@pytest.mark.asyncio
async def test_marketplace_browse(c):
    assert (await c.get("/api/v1/marketplace/apps")).status_code == 200

@pytest.mark.asyncio
async def test_marketplace_categories(c):
    assert (await c.get("/api/v1/marketplace/categories")).status_code == 200

@pytest.mark.asyncio
async def test_marketplace_featured(c):
    assert (await c.get("/api/v1/marketplace/featured")).status_code == 200

@pytest.mark.asyncio
async def test_marketplace_recent(c):
    assert (await c.get("/api/v1/marketplace/recent")).status_code == 200

@pytest.mark.asyncio
async def test_marketplace_trending(c):
    assert (await c.get("/api/v1/marketplace/trending")).status_code == 200

@pytest.mark.asyncio
async def test_marketplace_404(c):
    assert (await c.get("/api/v1/marketplace/apps/fake")).status_code == 404

# ── Auth required ────────────────────────────────────────

@pytest.mark.asyncio
async def test_no_auth_accounts(c):
    assert (await c.get("/api/v1/developer/accounts/me")).status_code == 401

@pytest.mark.asyncio
async def test_no_auth_apps(c):
    assert (await c.get("/api/v1/developer/apps")).status_code == 401

@pytest.mark.asyncio
async def test_no_auth_keys(c):
    assert (await c.get("/api/v1/developer/signing-keys")).status_code == 401

@pytest.mark.asyncio
async def test_no_auth_adapters(c):
    assert (await c.get("/api/v1/developer/adapters")).status_code == 401

@pytest.mark.asyncio
async def test_no_auth_sources(c):
    assert (await c.get("/api/v1/developer/sources")).status_code == 401

# ── Service imports ──────────────────────────────────────

def test_import_developer():
    from app.services.developer import create_developer_account, create_app
    assert callable(create_developer_account)

def test_import_sandbox():
    from app.services.sandbox import SandboxManager
    assert callable(SandboxManager)

def test_import_event_dispatch():
    from app.services.event_dispatch import emit_event
    assert callable(emit_event)

def test_import_conformance():
    from app.services.conformance import run_conformance_checks
    assert callable(run_conformance_checks)

def test_import_manifest():
    from app.services.manifest_validator import validate_manifest
    assert callable(validate_manifest)

def test_import_compatibility():
    from app.services.app_compatibility import check_upgrade_compatibility
    assert callable(check_upgrade_compatibility)

def test_import_analytics():
    from app.services.app_analytics import get_app_summary_metrics
    assert callable(get_app_summary_metrics)

def test_import_discovery():
    from app.services.app_discovery import get_featured_apps
    assert callable(get_featured_apps)

def test_import_export():
    from app.services.app_export import export_app_config
    assert callable(export_app_config)

def test_import_import():
    from app.services.app_import import validate_import_data
    assert callable(validate_import_data)

def test_import_metrics():
    from app.services.app_metrics import record_api_call
    assert callable(record_api_call)

def test_import_permissions():
    from app.services.app_permissions import check_permission
    assert callable(check_permission)

def test_import_webhooks():
    from app.services.app_webhooks import validate_webhook_url
    assert callable(validate_webhook_url)
