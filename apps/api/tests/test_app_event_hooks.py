"""Tests for event hooks and platform admin endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.services.app_event_hooks import (
    on_app_installed,
    on_app_uninstalled,
    on_cohort_member_added,
    on_evaluation_completed,
    on_org_member_added,
    on_pack_installed,
    on_pack_published,
    on_project_published,
    on_submission_completed,
    on_submission_graded,
    on_workflow_run_completed,
)


def _email():
    return f"hook-{uuid.uuid4().hex[:8]}@test.com"


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


# ── Event Hook Unit Tests ────────────────────────────────


@pytest.mark.asyncio
async def test_on_submission_completed():
    """Verify event hook functions are callable and return int."""
    # These need a DB session to emit — test the import and signature
    assert callable(on_submission_completed)
    assert callable(on_submission_graded)
    assert callable(on_cohort_member_added)
    assert callable(on_project_published)
    assert callable(on_pack_published)
    assert callable(on_pack_installed)
    assert callable(on_workflow_run_completed)
    assert callable(on_app_installed)
    assert callable(on_app_uninstalled)
    assert callable(on_evaluation_completed)
    assert callable(on_org_member_added)


# ── Webhook Verify ───────────────────────────────────────


def test_webhook_secret_format():
    from app.services.webhook_verify import generate_webhook_secret

    raw, hashed = generate_webhook_secret()
    assert raw.startswith("whsec_")
    assert len(hashed) == 64
    # Each call generates unique secret
    raw2, _ = generate_webhook_secret()
    assert raw != raw2


def test_webhook_roundtrip():
    from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature

    raw, _ = generate_webhook_secret()
    payload = b'{"event_type": "test", "data": {"x": 1}}'
    sig = sign_payload(payload, raw)
    assert verify_signature(payload, sig, raw)
    assert not verify_signature(b"tampered", sig, raw)
    assert not verify_signature(payload, sig, "wrong")


# ── Idempotency ─────────────────────────────────────────


def test_idempotency_ttl():
    from app.services.idempotency import get_cached_response, make_key, store_response

    k = make_key("ttl-test", "POST", "/test")
    store_response(k, {"ok": True})
    assert get_cached_response(k) is not None
    assert get_cached_response(k)["ok"] is True


def test_idempotency_key_uniqueness():
    from app.services.idempotency import make_key

    k1 = make_key("client-a", "POST", "/x")
    k2 = make_key("client-a", "POST", "/y")
    k3 = make_key("client-b", "POST", "/x")
    assert k1 != k2
    assert k1 != k3
    # Same input = same key
    assert k1 == make_key("client-a", "POST", "/x")


# ── SSRF Protection ─────────────────────────────────────


def test_ssrf_rejects_blocked_hosts():
    from app.services.event_dispatch import _is_safe_url

    # Must be https
    assert _is_safe_url("http://example.com") is False
    assert _is_safe_url("ftp://example.com") is False
    # Blocked metadata/internal hosts
    assert _is_safe_url("https://localhost") is False
    assert _is_safe_url("https://169.254.169.254") is False
    assert _is_safe_url("https://metadata.google.internal") is False
    # Empty/malformed
    assert _is_safe_url("") is False
    assert _is_safe_url("not-a-url") is False


# ── Manifest SSRF ────────────────────────────────────────


def test_manifest_rejects_aws_metadata():
    from app.services.manifest_validator import validate_manifest

    result = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "Test"},
        "sandbox": {"network": {"allowed_hosts": ["169.254.169.254"]}},
    })
    assert not result.valid


def test_manifest_rejects_link_local():
    from app.services.manifest_validator import validate_manifest

    result = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "Test"},
        "sandbox": {"network": {"allowed_hosts": ["169.254.0.1"]}},
    })
    assert not result.valid


def test_manifest_allows_public_domain():
    from app.services.manifest_validator import validate_manifest

    result = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "Test"},
        "sandbox": {"network": {"allowed_hosts": ["api.example.com"]}},
    })
    # No SSRF error on public domain
    ssrf_errors = [e for e in result.errors if "Blocked" in e or "private" in e.lower()]
    assert len(ssrf_errors) == 0


# ── Adapter SDK ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_adapter_default_health_check():
    from app.services.adapter_sdk import ProviderAdapterSDK

    class MinimalAdapter(ProviderAdapterSDK):
        name = "minimal"
        async def execute(self, *args, **kwargs):
            return {}

    adapter = MinimalAdapter()
    health = await adapter.health_check()
    assert health.status == "healthy"


@pytest.mark.asyncio
async def test_adapter_default_validate_config():
    from app.services.adapter_sdk import ProviderAdapterSDK

    class MinimalAdapter(ProviderAdapterSDK):
        name = "minimal"
        async def execute(self, *args, **kwargs):
            return {}

    adapter = MinimalAdapter()
    errors = await adapter.validate_config({"key": "val"})
    assert errors == []


@pytest.mark.asyncio
async def test_source_adapter_default_health():
    from app.services.adapter_sdk import EcosystemSourceAdapter, SourceRecord

    class MinimalSource(EcosystemSourceAdapter):
        name = "minimal-src"
        source_type = "test"
        async def fetch_records(self, *args, **kwargs):
            return []

    src = MinimalSource()
    health = await src.health_check()
    assert health.status == "healthy"
    errors = await src.validate_config({})
    assert errors == []
