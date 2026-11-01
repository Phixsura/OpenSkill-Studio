"""Error boundary — structured error responses for all marketplace API endpoints."""

from datetime import datetime, timezone

ERROR_CODES = {
    "APP_NOT_FOUND": {"status": 404, "message": "The requested app was not found"},
    "DEVELOPER_NOT_FOUND": {"status": 404, "message": "Developer profile not found"},
    "UNAUTHORIZED": {"status": 401, "message": "Authentication required"},
    "FORBIDDEN": {"status": 403, "message": "You don't have permission to perform this action"},
    "RATE_LIMITED": {"status": 429, "message": "Too many requests. Please try again later"},
    "VALIDATION_ERROR": {"status": 422, "message": "The request data is invalid"},
    "CONFLICT": {"status": 409, "message": "This action conflicts with the current state"},
    "INTERNAL_ERROR": {"status": 500, "message": "An unexpected error occurred"},
    "SERVICE_UNAVAILABLE": {"status": 503, "message": "The service is temporarily unavailable"},
}


def build_error_response(*, code: str, details: str | None = None, field: str | None = None) -> dict:
    error_def = ERROR_CODES.get(code, ERROR_CODES["INTERNAL_ERROR"])
    response = {"error": {"code": code, "message": error_def["message"],
                            "status": error_def["status"],
                            "timestamp": datetime.now(timezone.utc).isoformat()}}
    if details:
        response["error"]["details"] = details
    if field:
        response["error"]["field"] = field
    return response


def is_retryable(*, code: str) -> bool:
    retryable = {"RATE_LIMITED", "SERVICE_UNAVAILABLE", "INTERNAL_ERROR"}
    return code in retryable


def get_all_error_codes() -> list[dict]:
    return [{"code": k, **v} for k, v in ERROR_CODES.items()]
