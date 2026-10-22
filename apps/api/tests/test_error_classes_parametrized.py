"""Parametrized tests for all error classes."""

import pytest
from app.services.developer import (
    DeveloperNotFoundError, AppNotFoundError, AppVersionNotFoundError,
    InstallationNotFoundError, DuplicateSlugError, DuplicateVersionError,
    InvalidStateTransitionError, PermissionDeniedError,
    AlreadyInstalledError, ApiKeyNotFoundError,
)
from app.exceptions import AppError

ERRORS = [
    (DeveloperNotFoundError, 404, "DEVELOPER_NOT_FOUND"),
    (AppNotFoundError, 404, "APP_NOT_FOUND"),
    (AppVersionNotFoundError, 404, "APP_VERSION_NOT_FOUND"),
    (InstallationNotFoundError, 404, "INSTALLATION_NOT_FOUND"),
    (DuplicateSlugError, 409, "DUPLICATE_SLUG"),
    (DuplicateVersionError, 409, "DUPLICATE_VERSION"),
    (InvalidStateTransitionError, 422, "INVALID_STATE_TRANSITION"),
    (PermissionDeniedError, 403, "PERMISSION_DENIED"),
    (AlreadyInstalledError, 409, "ALREADY_INSTALLED"),
    (ApiKeyNotFoundError, 404, "API_KEY_NOT_FOUND"),
]

@pytest.mark.parametrize("cls,status,code", ERRORS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_error_status_code(cls, status, code):
    e = cls()
    assert e.status_code == status

@pytest.mark.parametrize("cls,status,code", ERRORS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_error_code(cls, status, code):
    e = cls()
    assert e.code == code

@pytest.mark.parametrize("cls,status,code", ERRORS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_error_is_app_error(cls, status, code):
    assert issubclass(cls, AppError)
