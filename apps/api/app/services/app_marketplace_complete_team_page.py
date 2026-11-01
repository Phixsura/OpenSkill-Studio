"""Complete team page — team management with invites, roles, and activity."""


def build_complete_team_page(*, team: list[dict], pending_invites: list[dict],
                                 activity: list[dict], plan_limit: int) -> dict:
    active = [m for m in team if m.get("status") == "active"]
    by_role = {}
    for m in active:
        r = m.get("role", "viewer")
        by_role[r] = by_role.get(r, 0) + 1
    return {
        "page_type": "team_management",
        "stats": {"total": len(active), "pending_invites": len(pending_invites),
                   "plan_limit": plan_limit, "seats_remaining": max(0, plan_limit - len(active)),
                   "by_role": by_role},
        "members": active,
        "pending": pending_invites,
        "recent_activity": activity[:10],
        "can_invite": len(active) < plan_limit,
    }
