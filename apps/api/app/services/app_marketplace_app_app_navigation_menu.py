"""Navigation menu — generate navigation menu structure."""


def build_navigation(*, user_role: str = "viewer", active_path: str = "/") -> dict:
    items = [
        {"path": "/", "label": "Home", "icon": "🏠", "roles": ["viewer", "developer", "admin"]},
        {"path": "/marketplace", "label": "Marketplace", "icon": "🏪", "roles": ["viewer", "developer", "admin"]},
        {"path": "/apps", "label": "My Apps", "icon": "📦", "roles": ["developer", "admin"]},
        {"path": "/analytics", "label": "Analytics", "icon": "📊", "roles": ["developer", "admin"]},
        {"path": "/webhooks", "label": "Webhooks", "icon": "🪝", "roles": ["developer", "admin"]},
        {"path": "/settings", "label": "Settings", "icon": "⚙️", "roles": ["viewer", "developer", "admin"]},
        {"path": "/docs", "label": "Documentation", "icon": "📚", "roles": ["viewer", "developer", "admin"]},
        {"path": "/admin", "label": "Admin Panel", "icon": "🔧", "roles": ["admin"]},
    ]
    visible = [i for i in items if user_role in i["roles"]]
    for item in visible:
        item["active"] = item["path"] == active_path
    return {"items": visible, "total": len(visible), "active_path": active_path}
