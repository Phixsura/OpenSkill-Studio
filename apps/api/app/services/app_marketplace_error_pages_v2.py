"""Error pages v2 — comprehensive error handling for all marketplace pages."""

ERROR_CONFIGS = {
    400: {"title": "Bad Request", "message": "The request couldn't be processed.", "icon": "🤔", "retryable": False},
    401: {"title": "Sign In Required", "message": "Please sign in to access this page.", "icon": "🔐", "retryable": False,
          "action": {"label": "Sign In", "url": "/login"}},
    403: {"title": "Access Denied", "message": "You don't have permission to view this.", "icon": "🚫", "retryable": False},
    404: {"title": "Page Not Found", "message": "We couldn't find what you're looking for.", "icon": "🔍", "retryable": False,
          "action": {"label": "Go Home", "url": "/marketplace"}},
    429: {"title": "Too Many Requests", "message": "Please slow down and try again.", "icon": "⏳", "retryable": True},
    500: {"title": "Something Went Wrong", "message": "We're working on fixing this.", "icon": "💥", "retryable": True},
    503: {"title": "Under Maintenance", "message": "We'll be back shortly.", "icon": "🔧", "retryable": True},
}


def build_error_page_v2(*, status_code: int, detail: str | None = None) -> dict:
    config = ERROR_CONFIGS.get(status_code, ERROR_CONFIGS[500])
    return {"status_code": status_code, **config, "detail": detail,
            "support_url": "/support" if status_code >= 500 else None}
