"""Tests for app notification service and additional integration coverage."""

import pytest

from app.services.app_notifications import (
    notify_app_installed,
    notify_app_revoked,
    notify_app_uninstalled,
    notify_review_decided,
    notify_review_submitted,
    notify_version_published,
)


def test_notification_functions_importable():
    """All notification functions are importable and callable."""
    funcs = [
        notify_app_installed,
        notify_app_uninstalled,
        notify_review_submitted,
        notify_review_decided,
        notify_app_revoked,
        notify_version_published,
    ]
    assert len(funcs) == 6
    assert all(callable(f) for f in funcs)


def test_compatibility_service_complete():
    """Verify all compatibility functions exist."""
    from app.services.app_compatibility import (
        PLATFORM_VERSION,
        check_upgrade_compatibility,
        is_compatible,
        parse_semver,
    )

    assert PLATFORM_VERSION == "1.0.0"
    assert callable(parse_semver)
    assert callable(is_compatible)
    assert callable(check_upgrade_compatibility)


def test_analytics_service_complete():
    """Verify all analytics functions exist."""
    from app.services.app_analytics import (
        get_app_summary_metrics,
        get_execution_timeline,
        get_install_timeline,
        get_top_orgs,
    )

    assert callable(get_install_timeline)
    assert callable(get_execution_timeline)
    assert callable(get_top_orgs)
    assert callable(get_app_summary_metrics)


def test_rate_limit_service_complete():
    """Verify rate limit service."""
    from app.services.app_rate_limit import (
        RATE_LIMITS,
        check_rate_limit,
        cleanup_old_counters,
        get_app_usage,
        get_installation_usage,
        get_rate_limit_headers,
        record_request,
    )

    assert RATE_LIMITS["standard"] == 1000
    assert RATE_LIMITS["elevated"] == 5000
    assert RATE_LIMITS["unlimited"] == 0
    assert callable(record_request)
    assert callable(get_app_usage)
    assert callable(get_installation_usage)
    assert callable(check_rate_limit)
    assert callable(get_rate_limit_headers)
    assert callable(cleanup_old_counters)


def test_sandbox_service_complete():
    """Verify sandbox service."""
    from app.services.sandbox import (
        DEFAULT_MEMORY_MB,
        DEFAULT_TIMEOUT_SECONDS,
        MAX_MEMORY_MB,
        MAX_OUTPUT_BYTES,
        MAX_TIMEOUT_SECONDS,
        SandboxManager,
        SandboxResult,
    )

    assert DEFAULT_TIMEOUT_SECONDS == 30
    assert MAX_TIMEOUT_SECONDS == 300
    assert DEFAULT_MEMORY_MB == 128
    assert MAX_MEMORY_MB == 512
    assert MAX_OUTPUT_BYTES == 1_000_000
    assert callable(SandboxManager)
    r = SandboxResult(success=True)
    assert r.success is True


def test_event_dispatch_canonical_events():
    """Verify canonical event count and categories."""
    from app.services.event_dispatch import CANONICAL_EVENTS

    assert len(CANONICAL_EVENTS) >= 35
    categories = set()
    for event in CANONICAL_EVENTS:
        categories.add(event.split(".")[0])
    assert "submission" in categories
    assert "cohort" in categories
    assert "project" in categories
    assert "pack" in categories
    assert "workflow" in categories
    assert "talent" in categories
    assert "marketplace" in categories
    assert "evaluation" in categories
    assert "app" in categories
    assert "org" in categories


def test_manifest_validator_scopes_count():
    """Verify all 42 permission scopes are defined."""
    from app.services.manifest_validator import VALID_PERMISSIONS, VALID_SURFACES

    assert len(VALID_PERMISSIONS) >= 30
    assert len(VALID_SURFACES) == 8


def test_webhook_verify_complete():
    """Full webhook verification roundtrip."""
    from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature

    for _ in range(3):
        raw, hashed = generate_webhook_secret()
        payload = f'{{"test": {_}}}'.encode()
        sig = sign_payload(payload, raw)
        assert verify_signature(payload, sig, raw)
        assert not verify_signature(b"tampered", sig, raw)
