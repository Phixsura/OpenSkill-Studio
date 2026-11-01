"""Parametrized platform version compatibility tests."""

import pytest
from app.services.app_compatibility import is_compatible, PLATFORM_VERSION

COMPATIBLE_VERSIONS = ["0.0.1", "0.1.0", "0.9.0", "0.99.99", "1.0.0"]
INCOMPATIBLE_VERSIONS = ["1.0.1", "1.1.0", "2.0.0", "5.0.0", "10.0.0", "99.99.99"]
NONE_VERSIONS = [None, ""]

@pytest.mark.parametrize("v", COMPATIBLE_VERSIONS)
def test_compatible(v):
    assert is_compatible(v) is True

@pytest.mark.parametrize("v", INCOMPATIBLE_VERSIONS)
def test_incompatible(v):
    assert is_compatible(v) is False

@pytest.mark.parametrize("v", NONE_VERSIONS)
def test_none_compatible(v):
    assert is_compatible(v) is True

def test_platform_version_is_1():
    assert PLATFORM_VERSION == "1.0.0"
