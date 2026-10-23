"""App marketplace header — marketplace navigation header."""

import html

NAV_ITEMS = [
    {"label": "Explore", "href": "/marketplace", "icon": "🏪"},
    {"label": "Categories", "href": "/categories", "icon": "📂"},
    {"label": "Trending", "href": "/trending", "icon": "🔥"},
    {"label": "Collections", "href": "/collections", "icon": "📚"},
    {"label": "Docs", "href": "/docs", "icon": "📖"},
]


def build_marketplace_header(*, user: dict | None = None, notifications: int = 0,
                                search_query: str = "", active_path: str = "") -> dict:
    nav = [{"label": n["label"], "href": n["href"], "icon": n["icon"],
            "active": n["href"] == active_path} for n in NAV_ITEMS]
    user_info = None
    if user:
        user_info = {"name": html.escape(user.get("name", "")),
                      "avatar": user.get("avatar"),
                      "initials": "".join(w[0].upper() for w in user.get("name", "?").split()[:2]),
                      "plan": user.get("plan", "free")}
    return {"nav": nav, "user": user_info, "notifications": notifications,
            "logged_in": user is not None, "search_query": search_query,
            "logo": {"text": "OpenSkill", "icon": "🧩"}}
