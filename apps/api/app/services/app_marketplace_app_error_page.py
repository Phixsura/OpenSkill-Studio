"""Error page — generate user-friendly error pages."""

import html


ERROR_PAGES = {
    400: {"title": "Bad Request", "icon": "🚫", "message": "The request was malformed or invalid."},
    401: {"title": "Unauthorized", "icon": "🔒", "message": "Please sign in to access this page."},
    403: {"title": "Forbidden", "icon": "⛔", "message": "You don't have permission to access this resource."},
    404: {"title": "Not Found", "icon": "🔍", "message": "The page you're looking for doesn't exist."},
    429: {"title": "Too Many Requests", "icon": "🐢", "message": "You've hit the rate limit. Please try again later."},
    500: {"title": "Server Error", "icon": "💥", "message": "Something went wrong on our end."},
    502: {"title": "Bad Gateway", "icon": "🌐", "message": "We're having trouble reaching the server."},
    503: {"title": "Service Unavailable", "icon": "🔧", "message": "The service is temporarily down for maintenance."},
}


def get_error_page(*, status_code: int, detail: str | None = None) -> dict:
    page = ERROR_PAGES.get(status_code, ERROR_PAGES[500])
    return {
        "status_code": status_code,
        "title": page["title"],
        "icon": page["icon"],
        "message": html.escape(detail) if detail else page["message"],
        "suggestions": _get_suggestions(status_code),
    }


def _get_suggestions(code: int) -> list[str]:
    if code == 404:
        return ["Check the URL for typos", "Go back to the homepage", "Use the search bar"]
    if code in (401, 403):
        return ["Sign in to your account", "Contact your admin for access"]
    if code == 429:
        return ["Wait a moment and try again", "Reduce request frequency"]
    if code >= 500:
        return ["Try refreshing the page", "Check the status page", "Contact support"]
    return ["Go back", "Try again"]
