"""API error page generator — generate structured error responses."""
from __future__ import annotations


ERROR_CODES = {
    400: {"code": "BAD_REQUEST", "message": "The request was invalid"},
    401: {"code": "UNAUTHORIZED", "message": "Authentication required"},
    403: {"code": "FORBIDDEN", "message": "Access denied"},
    404: {"code": "NOT_FOUND", "message": "Resource not found"},
    409: {"code": "CONFLICT", "message": "Resource conflict"},
    429: {"code": "RATE_LIMITED", "message": "Too many requests"},
    500: {"code": "INTERNAL_ERROR", "message": "An internal error occurred"},
    502: {"code": "BAD_GATEWAY", "message": "Bad gateway"},
    503: {"code": "SERVICE_UNAVAILABLE", "message": "Service temporarily unavailable"},
}


def generate_error(status: int, detail: str = "", request_id: str = "") -> dict:
    template = ERROR_CODES.get(status, {"code": "UNKNOWN", "message": "Unknown error"})
    return {"error": {"code": template["code"], "message": template["message"],
                       "detail": detail, "status": status, "request_id": request_id}}


def error_summary(errors: list[dict]) -> dict:
    by_code: dict[str, int] = {}
    for e in errors:
        code = e.get("error", {}).get("code", "UNKNOWN")
        by_code[code] = by_code.get(code, 0) + 1
    return {"total": len(errors), "by_code": by_code,
            "most_common": max(by_code.items(), key=lambda x: x[1])[0] if by_code else "none"}
