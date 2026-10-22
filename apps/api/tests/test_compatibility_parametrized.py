"""Parametrized platform compatibility tests."""

import pytest
from app.services.app_compatibility import is_compatible

COMPATIBLE = ["0.0.1", "0.1.0", "0.9.9", "1.0.0"]
INCOMPATIBLE = ["2.0.0", "5.0.0", "99.0.0", "10.0.0"]

@pytest.mark.parametrize("version", COMPATIBLE)
def test_compatible(version):
    assert is_compatible(version) is True

@pytest.mark.parametrize("version", INCOMPATIBLE)
def test_incompatible(version):
    assert is_compatible(version) is False

@pytest.mark.parametrize("version", [None, ""])
def test_no_requirement(version):
    assert is_compatible(version) is True
