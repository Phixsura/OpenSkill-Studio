"""Manifest with invalid permission formats."""

import pytest
from app.services.manifest_validator import validate_manifest

BASE = {
    "schema_version": "1.0",
    "app": {"name": "Perms", "slug": "perms-test", "version": "1.0.0", "category": "connector"},
}

INVALID_PERMS = [
    "admin:everything",
    "delete:users",
    "sudo:root",
    "execute:shell",
    "",
    "just_a_string",
    "read:",
    ":cohorts",
]

@pytest.mark.parametrize("perm", INVALID_PERMS)
def test_invalid_permission_flagged(perm):
    m = {**BASE, "permissions": [perm]}
    r = validate_manifest(m)
    assert not r.valid or len(r.errors) > 0 or len(r.warnings) > 0, f"{perm} should be flagged"

def test_mixed_valid_invalid():
    m = {**BASE, "permissions": ["read:cohorts", "admin:everything"]}
    r = validate_manifest(m)
    assert not r.valid or len(r.errors) > 0 or len(r.warnings) > 0
