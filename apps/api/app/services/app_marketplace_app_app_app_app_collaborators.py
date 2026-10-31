"""App collaborators — app-level collaborator management."""

import html

ROLES = {"owner": 4, "maintainer": 3, "contributor": 2, "tester": 1}
ROLE_ICONS = {"owner": "👑", "maintainer": "🛡️", "contributor": "✏️", "tester": "🧪"}


def build_collaborators_list(*, collaborators: list[dict], app_name: str) -> dict:
    items = []
    by_role: dict[str, int] = {}
    for c in collaborators:
        role = c.get("role", "contributor")
        by_role[role] = by_role.get(role, 0) + 1
        items.append({
            "id": c.get("id", ""), "name": html.escape(c.get("name", "")),
            "email": c.get("email", ""), "role": role,
            "role_icon": ROLE_ICONS.get(role, "👤"),
            "role_level": ROLES.get(role, 0),
            "can_deploy": ROLES.get(role, 0) >= 3,
            "can_publish": role == "owner",
        })
    items.sort(key=lambda x: -x["role_level"])
    return {"collaborators": items, "total": len(items),
            "by_role": by_role, "app_name": html.escape(app_name)}
