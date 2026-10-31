"""Developer Platform integration — verify all modules work together."""

import pytest
from app.services.manifest_validator import validate_manifest
from app.services.app_compatibility import check_upgrade_compatibility
from app.services.app_health_monitor import HealthScore
from app.services.conformance import ConformanceCheck, ConformanceReport
from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature
from app.services.app_metrics import increment, get_count
from app.services.app_rate_limit import check_rate_limit
from app.services.idempotency import make_key, store_response, get_cached_response


def test_manifest_to_compatibility_flow():
    """Validate manifest → check upgrade compatibility."""
    old_manifest = {
        "schema_version": "1.0",
        "app": {"name": "App", "slug": "app", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts"],
    }
    new_manifest = {
        "schema_version": "1.0",
        "app": {"name": "App", "slug": "app", "version": "2.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "write:cohorts"],
    }
    # Both valid
    assert validate_manifest(old_manifest).valid
    assert validate_manifest(new_manifest).valid
    # Compatible upgrade
    report = check_upgrade_compatibility(old_manifest, new_manifest)
    assert report["compatible"] is True
    assert "write:cohorts" in report["permissions_added"]


def test_health_to_conformance_flow():
    """Health score → conformance check integration."""
    health = HealthScore(1000, 10, 5)
    assert health.status == "degraded" or health.status == "healthy"

    check = ConformanceCheck(
        name="health",
        status="pass" if health.score >= 80 else "fail",
        message=f"Health score: {health.score}",
        details=health.to_dict(),
    )
    report = ConformanceReport(
        app_id="a", app_name="App", version="1.0.0",
        checked_at="2026-01-01T00:00:00Z", checks=[check],
    )
    assert report.passed is True


def test_webhook_to_metrics_flow():
    """Generate secret → sign → verify → record metric."""
    _, secret = generate_webhook_secret()
    payload = b'{"event":"test"}'
    sig = sign_payload(payload, secret)
    assert verify_signature(payload, sig, secret)

    # Record the delivery
    increment("webhook_delivered", "integration-app")
    assert get_count("webhook_delivered", "integration-app") >= 1


def test_rate_limit_to_idempotency_flow():
    """Check rate limit → idempotent response."""
    app_id = "integration-flow-app"
    assert check_rate_limit(app_id) is True

    key = make_key("client-int", "POST", "/api/v1/test")
    store_response(key, {"status": "created"}, 201)
    cached = get_cached_response(key)
    assert cached == {"status": "created"}
