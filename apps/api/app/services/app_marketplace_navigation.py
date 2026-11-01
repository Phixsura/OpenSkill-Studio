"""Marketplace navigation — build responsive navigation menus."""

MAIN_NAV = [
    {"id": "explore", "label": "Explore", "url": "/marketplace", "icon": "🏪"},
    {"id": "categories", "label": "Categories", "url": "/marketplace/categories", "icon": "📂"},
    {"id": "collections", "label": "Collections", "url": "/marketplace/collections", "icon": "📋"},
    {"id": "trending", "label": "Trending", "url": "/marketplace/trending", "icon": "🔥"},
]

DEV_NAV = [
    {"id": "dashboard", "label": "Dashboard", "url": "/developer", "icon": "📊"},
    {"id": "apps", "label": "My Apps", "url": "/developer/apps", "icon": "📦"},
    {"id": "analytics", "label": "Analytics", "url": "/developer/analytics", "icon": "📈"},
    {"id": "webhooks", "label": "Webhooks", "url": "/developer/webhooks", "icon": "🔗"},
    {"id": "team", "label": "Team", "url": "/developer/team", "icon": "👥"},
    {"id": "billing", "label": "Billing", "url": "/developer/billing", "icon": "💳"},
    {"id": "settings", "label": "Settings", "url": "/developer/settings", "icon": "⚙️"},
]


def get_main_nav(*, active_id: str | None = None) -> list[dict]:
    return [{**item, "active": item["id"] == active_id} for item in MAIN_NAV]


def get_developer_nav(*, active_id: str | None = None, app_count: int = 0,
                         notification_count: int = 0) -> list[dict]:
    nav = [{**item, "active": item["id"] == active_id} for item in DEV_NAV]
    for item in nav:
        if item["id"] == "apps":
            item["badge"] = str(app_count) if app_count > 0 else None
    return nav


def get_mobile_nav(*, is_developer: bool, active_id: str | None = None) -> list[dict]:
    items = list(MAIN_NAV)
    if is_developer:
        items.append({"id": "developer", "label": "Developer", "url": "/developer", "icon": "🛠️"})
    return [{**item, "active": item["id"] == active_id} for item in items]
