"""App team page — complete team management for an organization."""

import html

ROLES = {"owner": "👑", "admin": "🛡️", "editor": "✏️", "viewer": "👁️"}


def build_team_page(*, org_name: str, members: list[dict],
                      pending_invites: list[dict] | None = None) -> dict:
    items = []
    by_role: dict[str, int] = {}
    for m in members:
        role = m.get("role", "viewer")
        by_role[role] = by_role.get(role, 0) + 1
        items.append({
            "id": m.get("id", ""),
            "name": html.escape(m.get("name", "")),
            "email": m.get("email", ""),
            "role": role,
            "role_icon": ROLES.get(role, "👤"),
            "active": m.get("active", True),
            "joined_at": m.get("joined_at", ""),
        })
    items.sort(key=lambda x: -{"owner": 4, "admin": 3, "editor": 2, "viewer": 1}.get(x["role"], 0))
    invites = [{"email": html.escape(i.get("email", "")), "role": i.get("role", "viewer"),
                "sent_at": i.get("sent_at", "")} for i in (pending_invites or [])]
    return {"org_name": html.escape(org_name), "members": items,
            "total_members": len(items), "by_role": by_role,
            "pending_invites": invites, "pending_count": len(invites)}
