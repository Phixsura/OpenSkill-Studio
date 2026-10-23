"""Sidebar navigation builder — construct navigation tree with badges."""
from __future__ import annotations

NAV_ITEMS = [
    {"id": "dashboard", "label": "Dashboard", "icon": "🏠", "path": "/dashboard"},
    {"id": "apps", "label": "Apps", "icon": "📱", "path": "/apps", "badge": None},
    {"id": "analytics", "label": "Analytics", "icon": "📊", "path": "/analytics"},
    {"id": "webhooks", "label": "Webhooks", "icon": "🔗", "path": "/webhooks"},
    {"id": "deployments", "label": "Deployments", "icon": "🚀", "path": "/deployments"},
    {"id": "monitoring", "label": "Monitoring", "icon": "📈", "path": "/monitoring"},
    {"id": "team", "label": "Team", "icon": "👥", "path": "/team"},
    {"id": "billing", "label": "Billing", "icon": "💳", "path": "/billing"},
    {"id": "settings", "label": "Settings", "icon": "⚙️", "path": "/settings"},
    {"id": "docs", "label": "Docs", "icon": "📚", "path": "/docs"},
]


def build_sidebar(*, active: str = "dashboard", badges: dict | None = None) -> dict:
    items = []
    for item in NAV_ITEMS:
        badge_count = (badges or {}).get(item["id"])
        items.append({**item, "active": item["id"] == active,
                       "badge": badge_count})
    return {"items": items, "active": active, "total_items": len(items)}


def get_nav_item(item_id: str) -> dict | None:
    return next((i for i in NAV_ITEMS if i["id"] == item_id), None)
