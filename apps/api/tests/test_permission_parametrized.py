"""Parametrized tests for every valid permission scope."""

import pytest
from app.services.manifest_validator import VALID_PERMISSIONS, validate_manifest

ALL_PERMS = sorted(VALID_PERMISSIONS)

@pytest.mark.parametrize("perm", ALL_PERMS)
def test_valid_permission_accepted(perm):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": [perm]})
    unknown_errors = [e for e in r.errors if "Unknown permission" in e]
    assert unknown_errors == [], f"Permission '{perm}' wrongly rejected"

@pytest.mark.parametrize("perm", ALL_PERMS)
def test_permission_has_colon(perm):
    assert ":" in perm

@pytest.mark.parametrize("perm", ALL_PERMS)
def test_permission_is_lowercase(perm):
    assert perm == perm.lower()
