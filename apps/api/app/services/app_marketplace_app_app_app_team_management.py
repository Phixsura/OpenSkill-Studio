"""App team management — complete team management page builder."""

import html

ROLES = {
    "owner": {"label": "Owner", "level": 4, "icon": "👑", "color": "purple"},
    "admin": {"label": "Admin", "level": 3, "icon": "🛡️", "color": "blue"},
    "editor": {"label": "Editor", "level": 2, "icon": "✏️", "color": "green"},
    "viewer": {"label": "Viewer", "level": 1, "icon": "👁️", "color": "gray"},
}


def build_team_page(*, members: list[dict], pending_invites: int = 0,
                      max_members: int = 50) -> dict:
    items = []
    by_role: dict[str, int] = {}
    for m in members:
        role = m.get("role", "viewer")
        role_info = ROLES.get(role, ROLES["viewer"])
        by_role[role] = by_role.get(role, 0) + 1
        items.append({
            "id": m.get("id", ""), "name": html.escape(m.get("name", "")),
            "email": m.get("email", ""), "role": role,
            "role_label": role_info["label"], "role_icon": role_info["icon"],
            "avatar": m.get("avatar"), "active": m.get("active", True),
        })
    items.sort(key=lambda x: -ROLES.get(x["role"], {}).get("level", 0))
    return {"members": items, "total": len(items), "by_role": by_role,
            "pending_invites": pending_invites,
            "seats_remaining": max(0, max_members - len(items)),
            "can_invite": len(items) < max_members}
