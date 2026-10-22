"""Access control — role-based permissions for app management."""

ROLES = {
    "owner": {"can_edit", "can_delete", "can_publish", "can_transfer", "can_manage_team", "can_view_analytics"},
    "admin": {"can_edit", "can_publish", "can_view_analytics", "can_manage_team"},
    "developer": {"can_edit", "can_view_analytics"},
    "viewer": {"can_view_analytics"},
}


def check_permission(*, user_role: str, permission: str) -> bool:
    perms = ROLES.get(user_role, set())
    return permission in perms


def get_user_permissions(*, user_role: str) -> list[str]:
    return sorted(ROLES.get(user_role, set()))


def assign_role(*, app_id: str, user_id: str, role: str, assigned_by: str) -> dict:
    if role not in ROLES:
        return {"error": f"Invalid role. Use: {', '.join(sorted(ROLES.keys()))}"}
    return {"app_id": app_id, "user_id": user_id, "role": role,
            "assigned_by": assigned_by, "error": None}


def can_perform_action(*, user_role: str, action: str) -> dict:
    allowed = check_permission(user_role=user_role, permission=action)
    return {"allowed": allowed, "role": user_role, "action": action,
            "reason": None if allowed else f"Role '{user_role}' lacks '{action}' permission"}
