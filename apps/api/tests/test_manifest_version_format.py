"""Manifest version format validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

VALID = ["1.0.0", "0.1.0", "10.20.30", "1.0.0-alpha", "1.0.0-beta.1", "1.0.0-rc.1"]
INVALID = ["1.0", "abc", "v1.0.0", "1"]

@pytest.mark.parametrize("ver", VALID)
def test_valid_version(ver):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T", "version": ver}})
    ver_errors = [e for e in r.errors if "semver" in e.lower() or "version" in e]
    assert ver_errors == []

@pytest.mark.parametrize("ver", INVALID)
def test_invalid_version(ver):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T", "version": ver}})
    ver_errors = [e for e in r.errors if "semver" in e.lower() or "version" in e]
    assert len(ver_errors) >= 1
