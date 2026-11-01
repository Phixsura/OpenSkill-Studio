"""Platform header bar — top navigation with user menu and notifications."""
from __future__ import annotations
import html


def build_header(*, user_name: str, avatar_url: str = "", org_name: str = "",
                   unread_notifications: int = 0, plan: str = "free") -> dict:
    return {
        "user": {"name": html.escape(user_name), "avatar_url": avatar_url,
                 "initials": "".join(w[0].upper() for w in user_name.split()[:2]) if user_name else "?"},
        "org": {"name": html.escape(org_name)} if org_name else None,
        "notifications": {"unread": unread_notifications, "has_unread": unread_notifications > 0},
        "plan": {"name": plan, "badge": plan.upper(),
                 "is_free": plan == "free"},
        "nav_links": [
            {"label": "Dashboard", "path": "/dashboard"},
            {"label": "Apps", "path": "/apps"},
            {"label": "Docs", "path": "/docs"},
        ],
    }
