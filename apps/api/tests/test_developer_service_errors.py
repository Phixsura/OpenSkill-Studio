"""Developer service error classes."""

import pytest
from app.services.developer import (
    DeveloperNotFoundError, AppNotFoundError, AppVersionNotFoundError,
    InstallationNotFoundError, DuplicateSlugError, DuplicateVersionError,
    InvalidStateTransitionError, PermissionDeniedError,
    AlreadyInstalledError, ApiKeyNotFoundError,
)
from app.exceptions import AppError

ERRORS = [
    DeveloperNotFoundError,
    AppNotFoundError,
    AppVersionNotFoundError,
    InstallationNotFoundError,
    DuplicateSlugError,
    DuplicateVersionError,
    InvalidStateTransitionError,
    PermissionDeniedError,
    AlreadyInstalledError,
    ApiKeyNotFoundError,
]

@pytest.mark.parametrize("cls", ERRORS, ids=lambda c: c.__name__)
def test_is_app_error(cls):
    assert issubclass(cls, AppError)

@pytest.mark.parametrize("cls", ERRORS, ids=lambda c: c.__name__)
def test_instantiable(cls):
    err = cls()
    assert err is not None

@pytest.mark.parametrize("cls", ERRORS, ids=lambda c: c.__name__)
def test_has_status_code(cls):
    err = cls()
    assert hasattr(err, "status_code")
    assert isinstance(err.status_code, int)

@pytest.mark.parametrize("cls", ERRORS, ids=lambda c: c.__name__)
def test_has_code(cls):
    err = cls()
    assert hasattr(err, "code")
    assert isinstance(err.code, str)

@pytest.mark.parametrize("cls", ERRORS, ids=lambda c: c.__name__)
def test_has_message(cls):
    err = cls()
    assert hasattr(err, "message")
    assert len(err.message) > 0

def test_not_found_is_404():
    assert DeveloperNotFoundError().status_code == 404
    assert AppNotFoundError().status_code == 404

def test_duplicate_is_409():
    assert DuplicateSlugError().status_code == 409
    assert DuplicateVersionError().status_code == 409

def test_permission_denied_is_403():
    assert PermissionDeniedError().status_code == 403
