"""API error handler — standardized error responses."""


ERROR_CODES = {
    "NOT_FOUND": {"status": 404, "message": "Resource not found"},
    "UNAUTHORIZED": {"status": 401, "message": "Authentication required"},
    "FORBIDDEN": {"status": 403, "message": "Insufficient permissions"},
    "VALIDATION_ERROR": {"status": 422, "message": "Validation failed"},
    "RATE_LIMITED": {"status": 429, "message": "Too many requests"},
    "INTERNAL_ERROR": {"status": 500, "message": "Internal server error"},
    "CONFLICT": {"status": 409, "message": "Resource conflict"},
    "BAD_REQUEST": {"status": 400, "message": "Bad request"},
}


def create_error_response(*, code: str, detail: str | None = None,
                            field: str | None = None) -> dict:
    error_info = ERROR_CODES.get(code, ERROR_CODES["INTERNAL_ERROR"])
    error = {
        "error": {
            "code": code,
            "message": detail or error_info["message"],
            "status": error_info["status"],
        }
    }
    if field:
        error["error"]["field"] = field
    return error


def classify_exception(*, exc_type: str, message: str) -> dict:
    if "not found" in message.lower() or exc_type == "NotFoundError":
        return {"code": "NOT_FOUND", "status": 404}
    if "permission" in message.lower() or "forbidden" in message.lower():
        return {"code": "FORBIDDEN", "status": 403}
    if "valid" in message.lower():
        return {"code": "VALIDATION_ERROR", "status": 422}
    if "duplicate" in message.lower() or "conflict" in message.lower():
        return {"code": "CONFLICT", "status": 409}
    return {"code": "INTERNAL_ERROR", "status": 500}
