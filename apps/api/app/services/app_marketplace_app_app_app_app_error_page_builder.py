"""App error page builder — branded error pages for apps."""

import html

ERROR_TEMPLATES = {
    "not_found": {"code": 404, "title": "Page Not Found", "icon": "🔍",
                   "message": "The page you're looking for doesn't exist or has been moved."},
    "unauthorized": {"code": 401, "title": "Unauthorized", "icon": "🔒",
                      "message": "You need to log in to access this page."},
    "forbidden": {"code": 403, "title": "Access Denied", "icon": "⛔",
                   "message": "You don't have permission to access this resource."},
    "server_error": {"code": 500, "title": "Something Went Wrong", "icon": "💥",
                      "message": "We're working on fixing this. Please try again later."},
    "maintenance": {"code": 503, "title": "Under Maintenance", "icon": "🔧",
                     "message": "We're performing scheduled maintenance. We'll be back shortly."},
    "rate_limited": {"code": 429, "title": "Too Many Requests", "icon": "🐌",
                      "message": "You've exceeded the rate limit. Please wait and try again."},
}


def build_error_page(*, template: str, app_name: str = "OpenSkill",
                       custom_message: str | None = None,
                       request_id: str | None = None) -> dict:
    tmpl = ERROR_TEMPLATES.get(template, ERROR_TEMPLATES["server_error"])
    return {
        "code": tmpl["code"], "title": tmpl["title"], "icon": tmpl["icon"],
        "message": html.escape(custom_message) if custom_message else tmpl["message"],
        "app_name": html.escape(app_name),
        "request_id": request_id,
        "actions": [
            {"label": "Go Home", "href": "/", "primary": True},
            {"label": "Go Back", "href": "javascript:history.back()", "primary": False},
        ],
    }
