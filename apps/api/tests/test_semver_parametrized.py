"""Parametrized semver parsing tests."""

import pytest
from app.services.app_compatibility import parse_semver

VALID = [
    ("0.0.0", (0, 0, 0)),
    ("1.0.0", (1, 0, 0)),
    ("1.2.3", (1, 2, 3)),
    ("10.20.30", (10, 20, 30)),
    ("99.99.99", (99, 99, 99)),
    ("0.0.1", (0, 0, 1)),
    ("1.0.0-alpha", (1, 0, 0)),
    ("2.0.0-beta.1", (2, 0, 0)),
    ("1.0.0-rc.1", (1, 0, 0)),
    ("1.0.0+build", (1, 0, 0)),
]

INVALID = ["", "abc", "1.0", "1", "a.b.c", "v1.0.0"]


@pytest.mark.parametrize("version,expected", VALID)
def test_valid_semver(version, expected):
    assert parse_semver(version) == expected

@pytest.mark.parametrize("version", INVALID)
def test_invalid_semver(version):
    assert parse_semver(version) is None
