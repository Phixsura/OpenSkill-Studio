"""Semver parsing boundary tests."""

import pytest
from app.services.app_compatibility import parse_semver

VALID = [
    ("0.0.0", (0, 0, 0)),
    ("0.0.1", (0, 0, 1)),
    ("1.0.0", (1, 0, 0)),
    ("99.99.99", (99, 99, 99)),
    ("100.200.300", (100, 200, 300)),
]

INVALID = [
    "",
    "1",
    "1.0",
    "1.0.0.0",
    "v1.0.0",
    "abc",
    "1.0.a",
    "-1.0.0",
    "1.-1.0",
    "1.0.-1",
    " 1.0.0",
    "1.0.0 ",
]

@pytest.mark.parametrize("version,expected", VALID)
def test_valid_semver(version, expected):
    assert parse_semver(version) == expected

@pytest.mark.parametrize("version", INVALID)
def test_invalid_semver(version):
    result = parse_semver(version)
    assert result is None or isinstance(result, tuple)

def test_comparison():
    a = parse_semver("1.2.3")
    b = parse_semver("1.2.4")
    assert a < b

def test_major_comparison():
    a = parse_semver("1.9.9")
    b = parse_semver("2.0.0")
    assert a < b
