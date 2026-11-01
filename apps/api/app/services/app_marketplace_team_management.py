"""Team management — manage developer team members, roles, and invitations."""

from datetime import datetime, timezone


def invite_member(*, team_id: str, email: str, role: str, invited_by: str) -> dict:
    valid_roles = {"owner", "admin", "developer", "viewer"}
    if role not in valid_roles:
        return {"error": f"Invalid role. Use: {', '.join(sorted(valid_roles))}"}
    return {"team_id": team_id, "email": email, "role": role, "invited_by": invited_by,
            "status": "pending", "invited_at": datetime.now(timezone.utc).isoformat(), "error": None}


def update_member_role(*, member_id: str, new_role: str, updated_by: str) -> dict:
    valid_roles = {"admin", "developer", "viewer"}
    if new_role not in valid_roles:
        return {"error": "Cannot assign owner role"}
    return {"member_id": member_id, "role": new_role, "updated_by": updated_by, "error": None}


def get_team_summary(*, members: list[dict]) -> dict:
    by_role = {}
    for m in members:
        r = m.get("role", "viewer")
        by_role[r] = by_role.get(r, 0) + 1
    active = sum(1 for m in members if m.get("status") == "active")
    pending = sum(1 for m in members if m.get("status") == "pending")
    return {"total": len(members), "active": active, "pending": pending, "by_role": by_role}
