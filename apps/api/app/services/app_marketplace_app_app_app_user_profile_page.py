"""App user profile page — user profile with activity and apps."""

import html
import hashlib


def build_user_profile_page(*, user: dict, apps: list[dict],
                               activity_count: int = 0) -> dict:
    name = html.escape(user.get("name", ""))
    email = user.get("email", "").strip().lower()
    gravatar = f"https://gravatar.com/avatar/{hashlib.md5(email.encode()).hexdigest()}?d=identicon&s=128"
    total_installs = sum(a.get("installs", 0) for a in apps)
    return {
        "name": name,
        "email": email,
        "avatar_url": user.get("avatar_url") or gravatar,
        "bio": html.escape(user.get("bio", "")),
        "role": user.get("role", "developer"),
        "member_since": user.get("member_since", ""),
        "stats": {
            "apps": len(apps),
            "total_installs": total_installs,
            "activity_count": activity_count,
        },
        "recent_apps": [{"id": a.get("id"), "name": html.escape(a.get("name", "")),
                          "icon": a.get("icon", "📦")} for a in apps[:5]],
    }
