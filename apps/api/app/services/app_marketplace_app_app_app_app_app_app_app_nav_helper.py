"""Navigation helper — build platform navigation with access control."""
from __future__ import annotations

NAV_SECTIONS = [
    {"id": "overview", "label": "Overview", "icon": "🏠", "path": "/", "roles": ["*"]},
    {"id": "apps", "label": "Apps", "icon": "📱", "path": "/apps", "roles": ["*"]},
    {"id": "analytics", "label": "Analytics", "icon": "📊", "path": "/analytics", "roles": ["admin", "editor"]},
    {"id": "webhooks", "label": "Webhooks", "icon": "🔗", "path": "/webhooks", "roles": ["admin", "editor"]},
    {"id": "team", "label": "Team", "icon": "👥", "path": "/team", "roles": ["admin"]},
    {"id": "billing", "label": "Billing", "icon": "💳", "path": "/billing", "roles": ["admin"]},
    {"id": "settings", "label": "Settings", "icon": "⚙️", "path": "/settings", "roles": ["admin"]},
    {"id": "docs", "label": "Docs", "icon": "📚", "path": "/docs", "roles": ["*"]},
]


def get_nav_for_role(role: str) -> list[dict]:
    return [s for s in NAV_SECTIONS if "*" in s["roles"] or role in s["roles"]]


def get_active_section(path: str) -> str | None:
    for s in NAV_SECTIONS:
        if path == s["path"] or (s["path"] != "/" and path.startswith(s["path"])):
            return s["id"]
    return "overview" if path == "/" else None


def build_nav(*, role: str, active_path: str, badges: dict | None = None) -> dict:
    items = get_nav_for_role(role)
    active_id = get_active_section(active_path)
    result = []
    for item in items:
        result.append({**item, "active": item["id"] == active_id,
                        "badge": (badges or {}).get(item["id"])})
    return {"items": result, "count": len(result), "active": active_id}
