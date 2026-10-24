"""Token permissions — display and manage token-level permissions."""

import html

PERMISSION_GROUPS = {
    "Read": [
        {"id": "read:apps", "label": "View apps", "icon": "📦"},
        {"id": "read:analytics", "label": "View analytics", "icon": "📊"},
        {"id": "read:users", "label": "View users", "icon": "👤"},
        {"id": "read:webhooks", "label": "View webhooks", "icon": "🔗"},
    ],
    "Write": [
        {"id": "write:apps", "label": "Manage apps", "icon": "✏️"},
        {"id": "write:webhooks", "label": "Manage webhooks", "icon": "🔗"},
        {"id": "write:settings", "label": "Change settings", "icon": "⚙️"},
    ],
    "Admin": [
        {"id": "admin:billing", "label": "Manage billing", "icon": "💳"},
        {"id": "admin:members", "label": "Manage members", "icon": "👥"},
        {"id": "admin:delete", "label": "Delete resources", "icon": "🗑️"},
    ],
}


def build_token_permissions(*, granted: list[str]) -> dict:
    granted_set = set(granted)
    groups = {}
    total = 0
    total_granted = 0
    for group_name, perms in PERMISSION_GROUPS.items():
        items = []
        for p in perms:
            is_granted = p["id"] in granted_set
            if is_granted:
                total_granted += 1
            total += 1
            items.append({**p, "granted": is_granted})
        groups[group_name] = items
    return {"groups": groups, "total": total, "granted": total_granted,
            "has_admin": any(p in granted_set for p in ["admin:billing", "admin:members", "admin:delete"])}
