"""App access control — RBAC for app management."""


ROLES = {
    "owner": {"level": 100, "permissions": ["*"]},
    "admin": {"level": 80, "permissions": ["manage_settings", "manage_members", "publish", "edit", "view"]},
    "developer": {"level": 60, "permissions": ["publish", "edit", "view"]},
    "viewer": {"level": 20, "permissions": ["view"]},
}


def check_permission(*, role: str, permission: str) -> dict:
    role_def = ROLES.get(role)
    if not role_def:
        return {"allowed": False, "error": f"Unknown role: {role}"}
    allowed = "*" in role_def["permissions"] or permission in role_def["permissions"]
    return {"allowed": allowed, "role": role, "permission": permission}


def assign_role(*, user_id: str, app_id: str, role: str, assigner_role: str,
                   target_current_role: str | None = None) -> dict:
    if role not in ROLES or assigner_role not in ROLES:
        return {"success": False, "error": f"Invalid role: {role}"}
    if not check_permission(role=assigner_role, permission="manage_members")["allowed"]:
        return {"success": False, "error": "Not permitted to manage members"}
    assigner_level = ROLES.get(assigner_role, {}).get("level", 0)
    target_level = ROLES[role]["level"]
    if target_level >= assigner_level:
        return {"success": False, "error": "Cannot assign role equal or higher than your own"}
    return {"success": True, "user_id": user_id, "app_id": app_id, "role": role}


def list_members(*, app_id: str) -> dict:
    return {
        "app_id": app_id,
        "members": [
            {"user_id": "u1", "display_name": "Alice", "role": "owner", "joined": "2026-01-01"},
            {"user_id": "u2", "display_name": "Bob", "role": "developer", "joined": "2026-06-15"},
            {"user_id": "u3", "display_name": "Carol", "role": "viewer", "joined": "2026-09-01"},
        ],
        "total": 3,
    }
