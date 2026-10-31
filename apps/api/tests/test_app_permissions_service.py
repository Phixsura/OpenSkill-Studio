"""App permissions service tests."""

import pytest
from app.services.app_permissions import (
    check_permission,
    get_missing_permissions,
    get_permission_summary,
    PATH_PERMISSION_MAP,
    WRITE_PERMISSION_MAP,
)

RESOURCES = list(PATH_PERMISSION_MAP.keys())

@pytest.mark.parametrize("resource", RESOURCES)
def test_read_granted(resource):
    perm = PATH_PERMISSION_MAP[resource]
    assert check_permission([perm], resource) is True

@pytest.mark.parametrize("resource", RESOURCES)
def test_read_denied(resource):
    assert check_permission(["unrelated:scope"], resource) is False

WRITE_RESOURCES = list(WRITE_PERMISSION_MAP.keys())

@pytest.mark.parametrize("resource", WRITE_RESOURCES)
def test_write_granted(resource):
    perm = WRITE_PERMISSION_MAP[resource]
    assert check_permission([perm], resource, is_write=True) is True

@pytest.mark.parametrize("resource", WRITE_RESOURCES)
def test_write_denied(resource):
    assert check_permission([], resource, is_write=True) is False

def test_unknown_resource_allowed():
    assert check_permission([], "nonexistent_resource") is True

MISSING_CASES = [
    (["read:cohorts"], ["read:cohorts", "write:cohorts"], ["write:cohorts"]),
    (["read:cohorts", "write:cohorts"], ["read:cohorts", "write:cohorts"], []),
    ([], ["read:skills"], ["read:skills"]),
]

@pytest.mark.parametrize("granted,required,expected_missing", MISSING_CASES)
def test_get_missing_permissions(granted, required, expected_missing):
    result = get_missing_permissions(granted, required)
    assert set(result) == set(expected_missing)

def test_permission_summary():
    perms = ["read:cohorts", "write:projects", "subscribe:events"]
    summary = get_permission_summary(perms)
    assert isinstance(summary, dict)

def test_permission_summary_empty():
    assert isinstance(get_permission_summary([]), dict)
