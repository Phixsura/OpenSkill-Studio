"""App compatibility — semver parsing + upgrade checks."""

import pytest
from app.services.app_compatibility import parse_semver, is_compatible, check_upgrade_compatibility

VALID_VERSIONS = [
    ("1.0.0", (1, 0, 0)),
    ("2.3.4", (2, 3, 4)),
    ("0.1.0", (0, 1, 0)),
    ("10.20.30", (10, 20, 30)),
]

INVALID_VERSIONS = ["abc", "1.0", "1.0.0.0", "", "v1.0.0", "1.x.0"]

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

UPGRADE_CASES = [
    ("1.0.0", "1.0.1", True, "patch"),
    ("1.0.0", "1.1.0", True, "minor"),
    ("1.0.0", "2.0.0", False, "major"),
]

@pytest.mark.parametrize("old,new,compat,kind", UPGRADE_CASES, ids=lambda x: str(x)[:15])
def test_upgrade_compatibility(old, new, compat, kind):
    result = check_upgrade_compatibility(old, new)
    assert isinstance(result, dict)
    assert "compatible" in result or "breaking" in result
