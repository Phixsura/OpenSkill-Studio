"""Error code registry — standardized error codes with human-readable messages."""
from __future__ import annotations

ERROR_CODES = {
    "AUTH_001": {"message": "Invalid credentials", "status": 401, "category": "auth"},
    "AUTH_002": {"message": "Token expired", "status": 401, "category": "auth"},
    "AUTH_003": {"message": "Insufficient permissions", "status": 403, "category": "auth"},
    "APP_001": {"message": "App not found", "status": 404, "category": "apps"},
    "APP_002": {"message": "App already exists", "status": 409, "category": "apps"},
    "APP_003": {"message": "App limit exceeded", "status": 429, "category": "apps"},
    "API_001": {"message": "Rate limit exceeded", "status": 429, "category": "api"},
    "API_002": {"message": "Invalid request body", "status": 400, "category": "api"},
    "API_003": {"message": "Unsupported media type", "status": 415, "category": "api"},
    "SYS_001": {"message": "Internal server error", "status": 500, "category": "system"},
    "SYS_002": {"message": "Service unavailable", "status": 503, "category": "system"},
}


def get_error(code: str) -> dict:
    info = ERROR_CODES.get(code)
    if not info:
        return {"code": code, "message": "Unknown error", "status": 500, "category": "unknown"}
    return {"code": code, **info}


def build_error_response(code: str, *, detail: str = "") -> dict:
    err = get_error(code)
    return {"error": {"code": err["code"], "message": err["message"],
                       "detail": detail}, "status": err["status"]}


def list_codes(*, category: str | None = None) -> list[dict]:
    codes = [{"code": k, **v} for k, v in ERROR_CODES.items()]
    if category:
        codes = [c for c in codes if c["category"] == category]
    return codes
