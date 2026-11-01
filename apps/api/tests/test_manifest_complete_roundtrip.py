"""Manifest validation complete roundtrip — build, validate, check compatibility."""

from app.services.manifest_validator import validate_manifest
from app.services.app_compatibility import check_upgrade_compatibility, parse_semver


def test_build_validate_upgrade():
    v1 = {
        "schema_version": "1.0",
        "app": {"name": "Roundtrip", "slug": "roundtrip", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30},
    }
    v2 = {
        "schema_version": "1.0",
        "app": {"name": "Roundtrip", "slug": "roundtrip", "version": "2.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "write:cohorts", "subscribe:events"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60},
        "event_subscriptions": ["submission.completed"],
    }

    # Both valid
    assert validate_manifest(v1).valid
    assert validate_manifest(v2).valid

    # Semver parses
    assert parse_semver("1.0.0") < parse_semver("2.0.0")

    # Upgrade compatible
    report = check_upgrade_compatibility(v1, v2)
    assert report["compatible"] is True
    assert set(report["permissions_added"]) == {"write:cohorts", "subscribe:events"}
    assert report["permissions_removed"] == []


def test_downgrade_removes_permissions():
    v2 = {"permissions": ["read:cohorts", "write:cohorts"]}
    v1 = {"permissions": ["read:cohorts"]}
    report = check_upgrade_compatibility(v2, v1)
    assert "write:cohorts" in report["permissions_removed"]
