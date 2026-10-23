"""Global error handler — standardized error responses with context."""
from __future__ import annotations
import html


HTTP_ERRORS = {
    400: {"title": "Bad Request", "description": "The request was malformed or invalid."},
    401: {"title": "Unauthorized", "description": "Authentication is required."},
    403: {"title": "Forbidden", "description": "You don't have permission to access this resource."},
    404: {"title": "Not Found", "description": "The requested resource was not found."},
    409: {"title": "Conflict", "description": "The request conflicts with the current state."},
    422: {"title": "Validation Error", "description": "The request body failed validation."},
    429: {"title": "Rate Limited", "description": "Too many requests. Please try again later."},
    500: {"title": "Internal Error", "description": "An unexpected error occurred."},
    502: {"title": "Bad Gateway", "description": "The upstream service returned an invalid response."},
    503: {"title": "Service Unavailable", "description": "The service is temporarily unavailable."},
}


def build_error_page(status: int, *, detail: str = "", request_id: str = "") -> dict:
    info = HTTP_ERRORS.get(status, {"title": "Error", "description": "An error occurred."})
    return {
        "status": status, "title": info["title"],
        "description": info["description"],
        "detail": html.escape(detail[:500]) if detail else "",
        "request_id": request_id,
        "actions": _suggest_actions(status),
    }


def _suggest_actions(status: int) -> list[dict]:
    if status == 401:
        return [{"label": "Sign In", "action": "login"}, {"label": "Go Home", "action": "home"}]
    if status == 404:
        return [{"label": "Go Home", "action": "home"}, {"label": "Search", "action": "search"}]
    if status == 429:
        return [{"label": "Try Again", "action": "retry"}]
    return [{"label": "Go Home", "action": "home"}, {"label": "Report Issue", "action": "report"}]
