"""Manifest validator edge cases."""

import pytest
from app.services.manifest_validator import validate_manifest, VALID_PERMISSIONS, VALID_SURFACES, VALID_CATEGORIES, _BLOCKED_HOST_NAMES


def test_valid_permissions_count():
    assert len(VALID_PERMISSIONS) >= 40

def test_valid_surfaces_count():
    assert len(VALID_SURFACES) >= 7

def test_valid_categories_count():
    assert len(VALID_CATEGORIES) >= 7

def test_blocked_hosts_exist():
    assert len(_BLOCKED_HOST_NAMES) > 0
    assert "localhost" in _BLOCKED_HOST_NAMES or "127.0.0.1" in _BLOCKED_HOST_NAMES

# --- Edge cases ---

def test_missing_schema_version():
    r = validate_manifest({"app": {"name": "X", "slug": "x", "version": "1.0.0", "category": "connector"}})
    assert not r.valid

def test_missing_app_key():
    r = validate_manifest({"schema_version": "1.0"})
    assert not r.valid

def test_empty_manifest():
    r = validate_manifest({})
    assert not r.valid

def test_none_manifest():
    r = validate_manifest(None)
    assert not r.valid

INVALID_SLUGS = ["Has Space", "UPPER", "under_score!", "a" * 200]

@pytest.mark.parametrize("slug", INVALID_SLUGS)
def test_invalid_slug(slug):
    r = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "X", "slug": slug, "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts"],
    })
    assert not r.valid or len(r.warnings) > 0

BLOCKED = ["localhost", "127.0.0.1", "169.254.169.254", "metadata.google.internal"]

@pytest.mark.parametrize("host", BLOCKED)
def test_blocked_network_hosts(host):
    r = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "X", "slug": "x", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
                     "network": {"allowed_hosts": [host], "egress_policy": "allowlist"}},
    })
    assert not r.valid or len(r.errors) > 0
