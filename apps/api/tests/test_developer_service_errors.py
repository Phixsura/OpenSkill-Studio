"""Tests for developer service error classes."""

from app.services.developer import (
    AlreadyInstalledError,
    ApiKeyNotFoundError,
    AppNotFoundError,
    AppVersionNotFoundError,
    DeveloperNotFoundError,
    DuplicateSlugError,
    DuplicateVersionError,
    InstallationNotFoundError,
    InvalidStateTransitionError,
    PermissionDeniedError,
)


def test_developer_not_found():
    e = DeveloperNotFoundError()
    assert e.status_code == 404
    assert e.code == "DEVELOPER_NOT_FOUND"

def test_developer_not_found_custom():
    e = DeveloperNotFoundError("Custom msg")
    assert "Custom msg" in str(e)

def test_app_not_found():
    e = AppNotFoundError()
    assert e.status_code == 404

def test_version_not_found():
    e = AppVersionNotFoundError()
    assert e.status_code == 404

def test_installation_not_found():
    e = InstallationNotFoundError()
    assert e.status_code == 404

def test_duplicate_slug():
    e = DuplicateSlugError()
    assert e.status_code == 409

def test_duplicate_version():
    e = DuplicateVersionError()
    assert e.status_code == 409

def test_invalid_transition():
    e = InvalidStateTransitionError()
    assert e.status_code == 422

def test_invalid_transition_custom():
    e = InvalidStateTransitionError("draft → published not allowed")
    assert "draft" in str(e)

def test_permission_denied():
    e = PermissionDeniedError()
    assert e.status_code == 403

def test_already_installed():
    e = AlreadyInstalledError()
    assert e.status_code == 409

def test_api_key_not_found():
    e = ApiKeyNotFoundError()
    assert e.status_code == 404

def test_all_errors_are_app_errors():
    from app.exceptions import AppError
    errors = [
        DeveloperNotFoundError(), AppNotFoundError(), AppVersionNotFoundError(),
        InstallationNotFoundError(), DuplicateSlugError(), DuplicateVersionError(),
        InvalidStateTransitionError(), PermissionDeniedError(),
        AlreadyInstalledError(), ApiKeyNotFoundError(),
    ]
    for e in errors:
        assert isinstance(e, AppError), f"{type(e).__name__} is not AppError"
