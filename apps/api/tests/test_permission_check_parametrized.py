"""Parametrized permission check tests covering all resources."""

import pytest
from app.services.app_permissions import PATH_PERMISSION_MAP, WRITE_PERMISSION_MAP, check_permission

READ_RESOURCES = list(PATH_PERMISSION_MAP.items())
WRITE_RESOURCES = list(WRITE_PERMISSION_MAP.items())

@pytest.mark.parametrize("resource,perm", READ_RESOURCES)
def test_read_granted(resource, perm):
    assert check_permission([perm], resource, is_write=False) is True

@pytest.mark.parametrize("resource,perm", READ_RESOURCES)
def test_read_denied(resource, perm):
    assert check_permission([], resource, is_write=False) is False

@pytest.mark.parametrize("resource,perm", WRITE_RESOURCES)
def test_write_granted(resource, perm):
    assert check_permission([perm], resource, is_write=True) is True

@pytest.mark.parametrize("resource,perm", WRITE_RESOURCES)
def test_write_denied(resource, perm):
    assert check_permission([], resource, is_write=True) is False
