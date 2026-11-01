"""App header — global navigation header builder."""

import html


def build_header(*, user: dict | None = None, notifications: int = 0,
                   nav_items: list[dict] | None = None) -> dict:
    default_nav = [
        {"label": "Marketplace", "href": "/marketplace", "icon": "🏪"},
        {"label": "My Apps", "href": "/apps", "icon": "📦"},
        {"label": "Docs", "href": "/docs", "icon": "📝"},
    ]
    nav = nav_items or default_nav
    items = [{"label": html.escape(n["label"]), "href": n["href"],
              "icon": n.get("icon", "")} for n in nav]
    user_info = None
    if user:
        user_info = {"name": html.escape(user.get("name", "")),
                      "email": user.get("email", ""),
                      "avatar": user.get("avatar"),
                      "initials": "".join(w[0].upper() for w in user.get("name", "?").split()[:2])}
    return {"nav": items, "user": user_info, "notifications": notifications,
            "logged_in": user is not None, "logo": "OpenSkill"}
