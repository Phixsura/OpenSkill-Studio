"""App permissions service tests."""

import pytest
from app.services.app_permissions import (
    check_permission,
    get_missing_permissions,
    get_permission_summary,
)

VALID_PERMISSIONS = [
    "read:cohorts", "write:cohorts", "read:projects", "write:projects",
    "read:submissions", "write:evaluations", "read:skills", "read:analytics",
    "subscribe:events", "extend:ui", "run:background_jobs", "read:talent",
]

@pytest.mark.parametrize("perm", VALID_PERMISSIONS)
def test_check_valid_permission(perm):
    assert check_permission([perm], perm) is True

@pytest.mark.parametrize("perm", VALID_PERMISSIONS)
def test_check_missing_permission(perm):
    assert check_permission([], perm) is False

MISSING_CASES = [
    (["read:cohorts"], ["read:cohorts", "write:cohorts"], ["write:cohorts"]),
    (["read:cohorts", "write:cohorts"], ["read:cohorts", "write:cohorts"], []),
    ([], ["read:skills"], ["read:skills"]),
]

@pytest.mark.parametrize("granted,required,expected_missing", MISSING_CASES)
def test_get_missing_permissions(granted, required, expected_missing):
    result = get_missing_permissions(granted, required)
    assert set(result) == set(expected_missing)

def test_permission_summary_groups():
    perms = ["read:cohorts", "write:projects", "subscribe:events", "extend:ui"]
    summary = get_permission_summary(perms)
    assert isinstance(summary, dict)

def test_permission_summary_empty():
    summary = get_permission_summary([])
    assert isinstance(summary, dict)
