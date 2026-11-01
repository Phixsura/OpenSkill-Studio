"""Error page — HTTP error page content generator."""

import html

ERROR_PAGES = {
    400: {"title": "Bad Request", "icon": "🚫", "description": "The request was malformed or invalid."},
    401: {"title": "Unauthorized", "icon": "🔒", "description": "You need to log in to access this resource."},
    403: {"title": "Forbidden", "icon": "⛔", "description": "You don't have permission to access this resource."},
    404: {"title": "Not Found", "icon": "🔍", "description": "The page you're looking for doesn't exist."},
    429: {"title": "Too Many Requests", "icon": "🐌", "description": "You've exceeded the rate limit. Please try again later."},
    500: {"title": "Internal Server Error", "icon": "💥", "description": "Something went wrong on our end."},
    502: {"title": "Bad Gateway", "icon": "🌐", "description": "The upstream server returned an invalid response."},
    503: {"title": "Service Unavailable", "icon": "🔧", "description": "The service is temporarily unavailable. Please try again later."},
}


def build_error_page(*, status_code: int, custom_message: str | None = None,
                       request_id: str | None = None) -> dict:
    page = ERROR_PAGES.get(status_code, {"title": "Error", "icon": "❌", "description": "An unknown error occurred."})
    return {"status_code": status_code, "title": page["title"], "icon": page["icon"],
            "description": html.escape(custom_message) if custom_message else page["description"],
            "request_id": request_id,
            "suggestions": _get_suggestions(status_code)}


def _get_suggestions(code: int) -> list[str]:
    if code == 404:
        return ["Check the URL for typos", "Go back to the homepage", "Search for what you need"]
    if code == 401:
        return ["Log in to your account", "Check your API key"]
    if code == 429:
        return ["Wait a moment and try again", "Reduce request frequency"]
    if code >= 500:
        return ["Try again in a few minutes", "Check the status page", "Contact support"]
    return ["Go back", "Try again"]
