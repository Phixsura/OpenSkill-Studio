"""Permission matrix — role-based access control grid."""

import html

ROLES = ["viewer", "editor", "admin", "owner"]
ACTIONS = ["read", "write", "delete", "manage_users", "billing"]

DEFAULT_MATRIX = {
    "viewer":  {"read": True, "write": False, "delete": False, "manage_users": False, "billing": False},
    "editor":  {"read": True, "write": True,  "delete": False, "manage_users": False, "billing": False},
    "admin":   {"read": True, "write": True,  "delete": True,  "manage_users": True,  "billing": False},
    "owner":   {"read": True, "write": True,  "delete": True,  "manage_users": True,  "billing": True},
}


def build_permission_matrix(*, overrides: dict | None = None) -> dict:
    matrix = {}
    for role in ROLES:
        base = dict(DEFAULT_MATRIX[role])
        if overrides and role in overrides:
            base.update(overrides[role])
        matrix[role] = base
    return {"matrix": matrix, "roles": ROLES, "actions": ACTIONS}


def check_permission(*, role: str, action: str, overrides: dict | None = None) -> dict:
    m = build_permission_matrix(overrides=overrides)
    allowed = m["matrix"].get(role, {}).get(action, False)
    return {"role": role, "action": action, "allowed": allowed}
