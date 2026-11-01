"""Marketplace header — navigation header data for all marketplace pages."""


def build_marketplace_header(*, user: dict | None, cart_count: int = 0,
                                notification_count: int = 0) -> dict:
    nav_items = [
        {"label": "Explore", "url": "/marketplace", "icon": "🏪"},
        {"label": "Categories", "url": "/marketplace/categories", "icon": "📂"},
        {"label": "Collections", "url": "/marketplace/collections", "icon": "📋"},
    ]
    if user:
        nav_items.append({"label": "My Apps", "url": "/marketplace/installed", "icon": "📦"})
    return {
        "nav_items": nav_items, "search_enabled": True,
        "user": {"name": user.get("display_name"), "avatar": user.get("avatar")} if user else None,
        "notification_count": notification_count, "is_developer": user.get("is_developer", False) if user else False,
    }
