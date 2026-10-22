"""Full manifest lifecycle — create v1 → validate → upgrade to v2 → validate → check compatibility."""

from app.services.manifest_validator import validate_manifest
from app.services.app_compatibility import check_upgrade_compatibility, parse_semver
from app.services.app_health_monitor import HealthScore
from app.services.conformance import ConformanceCheck, ConformanceReport


def test_full_lifecycle():
    # v1: basic connector
    v1 = {
        "schema_version": "1.0",
        "app": {"name": "Lifecycle App", "slug": "lifecycle", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts"],
    }
    assert validate_manifest(v1).valid

    # v2: adds features
    v2 = {
        "schema_version": "1.0",
        "app": {"name": "Lifecycle App", "slug": "lifecycle", "version": "2.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "write:cohorts", "subscribe:events", "extend:ui"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60,
                     "network": {"allowed_hosts": ["api.example.com"], "egress_policy": "allowlist"}},
        "event_subscriptions": ["submission.completed"],
        "ui_extensions": [{"surface": "dashboard_card", "title": "Stats", "entry": "stats.html"}],
    }
    assert validate_manifest(v2).valid

    # Version ordering
    assert parse_semver("1.0.0") < parse_semver("2.0.0")

    # Upgrade report
    report = check_upgrade_compatibility(v1, v2)
    assert report["compatible"]
    assert set(report["permissions_added"]) == {"write:cohorts", "subscribe:events", "extend:ui"}

    # Health check
    health = HealthScore(500, 5, 2)
    assert health.status == "healthy"

    # Conformance
    checks = [
        ConformanceCheck(name="manifest", status="pass", message="Valid v2", details={}),
        ConformanceCheck(name="health", status="pass", message=f"Score: {health.score}", details=health.to_dict()),
    ]
    cr = ConformanceReport(app_id="lifecycle", app_name="Lifecycle App", version="2.0.0", checked_at="now", checks=checks)
    assert cr.passed
    assert cr.summary["total_checks"] == 2
