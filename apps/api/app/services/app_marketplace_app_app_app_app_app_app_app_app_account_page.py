"""Account page — complete user account settings page."""

import html
import hashlib


def build_account_page(*, user: dict, sessions: list[dict] | None = None,
                          connected_accounts: list[dict] | None = None) -> dict:
    email = user.get("email", "").strip().lower()
    gravatar = f"https://gravatar.com/avatar/{hashlib.md5(email.encode()).hexdigest()}?d=identicon&s=128"
    active_sessions = len(sessions or [])
    connections = [{"provider": html.escape(c.get("provider", "")),
                     "connected": c.get("connected", False),
                     "username": html.escape(c.get("username", ""))}
                    for c in (connected_accounts or [])]
    return {
        "profile": {
            "name": html.escape(user.get("name", "")),
            "email": email,
            "avatar_url": user.get("avatar_url") or gravatar,
            "bio": html.escape(user.get("bio", "")),
            "timezone": user.get("timezone", "UTC"),
        },
        "security": {
            "two_factor_enabled": user.get("two_factor", False),
            "active_sessions": active_sessions,
            "password_updated": user.get("password_updated", "Never"),
        },
        "connected_accounts": connections,
        "connected_count": sum(1 for c in connections if c["connected"]),
        "sections": ["profile", "security", "connected_accounts", "notifications", "danger_zone"],
    }
