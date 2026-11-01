"""App global nav — top-level navigation bar for the entire platform."""

import html

PRIMARY_NAV = [
    {"id": "marketplace", "label": "Marketplace", "href": "/marketplace", "icon": "🏪"},
    {"id": "console", "label": "Console", "href": "/console", "icon": "💻"},
    {"id": "docs", "label": "Docs", "href": "/docs", "icon": "📖"},
    {"id": "community", "label": "Community", "href": "/community", "icon": "💬"},
]

USER_MENU = [
    {"label": "Profile", "href": "/profile", "icon": "👤"},
    {"label": "Settings", "href": "/settings", "icon": "⚙️"},
    {"label": "Billing", "href": "/billing", "icon": "💳"},
    {"label": "Log out", "href": "/logout", "icon": "👋"},
]


def build_global_nav(*, user: dict | None = None, active_section: str = "",
                       notifications: int = 0) -> dict:
    nav = [{"id": n["id"], "label": n["label"], "href": n["href"], "icon": n["icon"],
            "active": n["id"] == active_section} for n in PRIMARY_NAV]
    user_info = None
    if user:
        user_info = {
            "name": html.escape(user.get("name", "")),
            "initials": "".join(w[0].upper() for w in user.get("name", "?").split()[:2]),
            "email": user.get("email", ""),
            "plan": user.get("plan", "free"),
            "menu": USER_MENU,
        }
    return {"nav": nav, "user": user_info, "logged_in": user is not None,
            "notifications": notifications,
            "logo": {"text": "OpenSkill", "icon": "🧩"},
            "search_placeholder": "Search apps, docs, APIs..."}
