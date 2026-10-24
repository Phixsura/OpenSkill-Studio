"""Permission maps completeness tests."""

import pytest
from app.services.app_permissions import PATH_PERMISSION_MAP, WRITE_PERMISSION_MAP, check_permission

def test_all_write_resources_have_read():
    """Every writable resource should also be readable."""
    for resource in WRITE_PERMISSION_MAP:
        assert resource in PATH_PERMISSION_MAP, f"{resource} writable but not readable"

def test_read_permissions_format():
    for resource, perm in PATH_PERMISSION_MAP.items():
        assert perm.startswith("read:"), f"{resource} → {perm} should start with read:"

def test_write_permissions_format():
    for resource, perm in WRITE_PERMISSION_MAP.items():
        assert perm.startswith("write:"), f"{resource} → {perm} should start with write:"

def test_no_empty_resources():
    for resource in PATH_PERMISSION_MAP:
        assert len(resource) > 0
    for resource in WRITE_PERMISSION_MAP:
        assert len(resource) > 0

CORE_RESOURCES = ["cohorts", "projects", "submissions", "skills", "analytics"]

@pytest.mark.parametrize("resource", CORE_RESOURCES)
def test_core_resource_readable(resource):
    assert resource in PATH_PERMISSION_MAP

@pytest.mark.parametrize("resource", ["cohorts", "projects", "skills"])
def test_core_resource_writable(resource):
    assert resource in WRITE_PERMISSION_MAP

def test_read_check_denies_without_perm():
    assert check_permission([], "cohorts") is False

def test_write_check_denies_without_perm():
    assert check_permission([], "cohorts", is_write=True) is False
