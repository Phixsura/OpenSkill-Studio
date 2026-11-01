"""Parametrized missing permission tests."""

import pytest
from app.services.app_permissions import get_missing_permissions

CASES = [
    ([], [], []),
    (["read:cohorts"], ["read:cohorts"], []),
    (["read:cohorts"], ["read:cohorts", "write:projects"], ["write:projects"]),
    ([], ["read:cohorts"], ["read:cohorts"]),
    (["read:cohorts", "write:projects"], ["read:cohorts"], []),
    (["a", "b"], ["a", "b", "c", "d"], ["c", "d"]),
]

@pytest.mark.parametrize("granted,required,expected", CASES)
def test_missing_permissions(granted, required, expected):
    assert get_missing_permissions(granted, required) == expected
