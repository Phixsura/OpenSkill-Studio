"""App team management — manage collaborators on marketplace apps."""
from __future__ import annotations
import html

ROLES = ["owner", "admin", "developer", "viewer"]


def build_team_list(members: list[dict]) -> dict:
    items = [{"name": html.escape(m.get("name", "")), "email": m.get("email", ""),
              "role": m.get("role", "viewer"), "avatar_initials": _initials(m.get("name", "")),
              "joined": m.get("joined", "")} for m in members]
    by_role = {}
    for item in items:
        by_role.setdefault(item["role"], []).append(item)
    return {"members": items, "total": len(items), "by_role": by_role,
            "roles": ROLES}


def can_manage(actor_role: str, target_role: str) -> bool:
    order = {r: i for i, r in enumerate(ROLES)}
    return order.get(actor_role, 99) < order.get(target_role, 99)


def _initials(name: str) -> str:
    return "".join(w[0].upper() for w in name.split()[:2]) if name else "?"
