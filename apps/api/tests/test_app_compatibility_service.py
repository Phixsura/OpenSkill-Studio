"""App compatibility — semver parsing + upgrade checks."""

import pytest
from app.services.app_compatibility import parse_semver, is_compatible, check_upgrade_compatibility

VALID_VERSIONS = [
    ("1.0.0", (1, 0, 0)),
    ("2.3.4", (2, 3, 4)),
    ("0.1.0", (0, 1, 0)),
    ("10.20.30", (10, 20, 30)),
]

INVALID_VERSIONS = ["abc", "1.0", "", "v1.0.0", "1.x.0"]

@pytest.mark.parametrize("version,expected", VALID_VERSIONS)
def test_parse_valid(version, expected):
    assert parse_semver(version) == expected

@pytest.mark.parametrize("version", INVALID_VERSIONS)
def test_parse_invalid(version):
    assert parse_semver(version) is None

def test_is_compatible_none():
    assert is_compatible(None) is True

def test_is_compatible_low_version():
    assert is_compatible("0.0.1") is True

def test_upgrade_no_breaking_changes():
    old = {"permissions": ["read:cohorts"]}
    new = {"permissions": ["read:cohorts", "read:projects"]}
    result = check_upgrade_compatibility(old, new)
    assert result["compatible"] is True
    assert "read:projects" in result["permissions_added"]

def test_upgrade_permission_removed():
    old = {"permissions": ["read:cohorts", "write:cohorts"]}
    new = {"permissions": ["read:cohorts"]}
    result = check_upgrade_compatibility(old, new)
    assert "write:cohorts" in result["permissions_removed"]

def test_upgrade_both_none():
    result = check_upgrade_compatibility(None, None)
    assert result["compatible"] is True

def test_upgrade_empty_manifests():
    result = check_upgrade_compatibility({}, {})
    assert result["compatible"] is True
