"""Manifest version format validation."""

import pytest
from app.services.manifest_validator import validate_manifest

BASE = {
    "schema_version": "1.0",
    "app": {"name": "X", "slug": "ver-test", "category": "connector"},
    "permissions": ["read:cohorts"],
}

VALID_VERSIONS = ["0.1.0", "1.0.0", "2.3.4", "10.20.30", "1.0.0-beta"]

@pytest.mark.parametrize("ver", VALID_VERSIONS)
def test_valid_version(ver):
    m = {**BASE, "app": {**BASE["app"], "version": ver}}
    r = validate_manifest(m)
    ver_errors = [e for e in r.errors if "version" in e.lower()]
    assert ver_errors == [], f"Version {ver} rejected: {ver_errors}"

INVALID_VERSIONS = ["abc"]

@pytest.mark.parametrize("ver", INVALID_VERSIONS)
def test_invalid_version(ver):
    m = {**BASE, "app": {**BASE["app"], "version": ver}}
    r = validate_manifest(m)
    assert not r.valid or len(r.errors) > 0 or len(r.warnings) > 0

