"""Error code registry — centralized error codes for developer platform API."""

ERROR_CODES = {
    "APP_NOT_FOUND": {"status": 404, "message": "App not found"},
    "VERSION_NOT_FOUND": {"status": 404, "message": "App version not found"},
    "INSTALLATION_NOT_FOUND": {"status": 404, "message": "Installation not found"},
    "DEVELOPER_NOT_FOUND": {"status": 404, "message": "Developer account not found"},
    "DUPLICATE_SLUG": {"status": 409, "message": "Slug already taken"},
    "DUPLICATE_VERSION": {"status": 409, "message": "Version already exists"},
    "ALREADY_INSTALLED": {"status": 409, "message": "App already installed in this org"},
    "INVALID_STATE_TRANSITION": {"status": 422, "message": "Invalid app state transition"},
    "PERMISSION_DENIED": {"status": 403, "message": "Permission denied"},
    "INVALID_MANIFEST": {"status": 422, "message": "Invalid manifest"},
    "RATE_LIMITED": {"status": 429, "message": "Rate limit exceeded"},
    "QUOTA_EXCEEDED": {"status": 429, "message": "Resource quota exceeded"},
    "APP_REVOKED": {"status": 403, "message": "App has been revoked"},
    "KEY_EXPIRED": {"status": 401, "message": "API key expired"},
    "INVALID_SCOPE": {"status": 403, "message": "Insufficient scope"},
}


def get_error(code: str) -> dict:
    err = ERROR_CODES.get(code, {"status": 500, "message": "Internal error"})
    return {"code": code, **err}


def list_error_codes() -> list[str]:
    return sorted(ERROR_CODES.keys())
