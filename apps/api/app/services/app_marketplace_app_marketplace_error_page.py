"""Error page — user-friendly error pages for marketplace."""


def build_error_page(*, status_code: int, message: str | None = None) -> dict:
    defaults = {
        400: {"title": "Bad Request", "message": "The request was malformed.", "icon": "🤔"},
        401: {"title": "Unauthorized", "message": "Please sign in to continue.", "icon": "🔐"},
        403: {"title": "Forbidden", "message": "You don't have access to this resource.", "icon": "🚫"},
        404: {"title": "Not Found", "message": "The page you're looking for doesn't exist.", "icon": "🔍"},
        429: {"title": "Too Many Requests", "message": "Slow down! Try again in a moment.", "icon": "⏳"},
        500: {"title": "Server Error", "message": "Something went wrong on our end.", "icon": "💥"},
        503: {"title": "Maintenance", "message": "We're performing maintenance. Back soon!", "icon": "🔧"},
    }
    default = defaults.get(status_code, {"title": "Error", "message": "An error occurred.", "icon": "❌"})
    return {"status_code": status_code, "title": default["title"],
            "message": message or default["message"], "icon": default["icon"],
            "show_home_link": True, "show_support_link": status_code >= 500}
