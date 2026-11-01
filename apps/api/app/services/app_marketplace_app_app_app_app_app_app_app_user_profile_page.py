"""User profile page — build the complete user profile view."""
from __future__ import annotations
import html


def build_user_profile(user: dict) -> dict:
    name = html.escape(user.get("name", ""))
    apps = user.get("apps", [])
    total_installs = sum(a.get("installs", 0) for a in apps)
    return {
        "name": name, "email": user.get("email", ""),
        "avatar_initials": "".join(w[0].upper() for w in name.split()[:2]) if name else "?",
        "role": user.get("role", "member"),
        "plan": user.get("plan", "free"),
        "joined": user.get("joined", ""),
        "app_count": len(apps),
        "total_installs": total_installs,
        "installs_display": f"{total_installs:,}",
        "badges": user.get("badges", []),
        "org": user.get("org", ""),
    }
