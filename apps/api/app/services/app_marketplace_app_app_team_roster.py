"""Team roster — team member management with roles."""

import html
from datetime import datetime, timezone

ROLES = {"owner": 4, "admin": 3, "editor": 2, "viewer": 1}


def build_team_roster(*, members: list[dict]) -> dict:
    items = []
    for m in members:
        role = m.get("role", "viewer")
        items.append({
            "id": m.get("id", ""),
            "name": html.escape(m.get("name", "")),
            "email": m.get("email", ""),
            "role": role,
            "role_level": ROLES.get(role, 0),
            "avatar_url": m.get("avatar_url"),
            "joined_at": m.get("joined_at", datetime.now(timezone.utc).isoformat()),
            "active": m.get("active", True),
        })
    items.sort(key=lambda x: -x["role_level"])
    by_role = {}
    for i in items:
        by_role[i["role"]] = by_role.get(i["role"], 0) + 1
    return {"members": items, "total": len(items),
            "active": sum(1 for i in items if i["active"]),
            "by_role": by_role}
