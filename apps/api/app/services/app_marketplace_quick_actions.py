"""Quick actions — context-aware action menus for marketplace entities."""


def get_app_quick_actions(*, app: dict, user_role: str) -> list[dict]:
    actions = []
    status = app.get("status", "draft")
    if status == "draft":
        actions.append({"id": "edit", "label": "Edit App", "icon": "✏️", "url": f"/developer/apps/{app['id']}/edit"})
        actions.append({"id": "submit", "label": "Submit for Review", "icon": "📤", "primary": True})
    elif status == "published":
        actions.append({"id": "analytics", "label": "View Analytics", "icon": "📊", "url": f"/developer/apps/{app['id']}/analytics"})
        actions.append({"id": "new_version", "label": "New Version", "icon": "🆕"})
    if user_role in ("owner", "admin"):
        actions.append({"id": "settings", "label": "Settings", "icon": "⚙️", "url": f"/developer/apps/{app['id']}/settings"})
        if status != "archived":
            actions.append({"id": "archive", "label": "Archive", "icon": "📦", "danger": True})
    return actions


def get_installation_quick_actions(*, installation: dict) -> list[dict]:
    actions = [
        {"id": "configure", "label": "Configure", "icon": "⚙️"},
        {"id": "logs", "label": "View Logs", "icon": "📋"},
        {"id": "webhooks", "label": "Webhooks", "icon": "🔗"},
    ]
    if installation.get("update_available"):
        actions.insert(0, {"id": "update", "label": "Update Available", "icon": "🔄", "primary": True})
    actions.append({"id": "uninstall", "label": "Uninstall", "icon": "🗑️", "danger": True})
    return actions
