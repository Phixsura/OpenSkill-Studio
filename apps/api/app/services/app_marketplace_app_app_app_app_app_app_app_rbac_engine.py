"""RBAC policy engine — role-based access control with inheritance."""
from __future__ import annotations

ROLE_HIERARCHY = {
    "superadmin": {"inherits": "admin", "level": 100},
    "admin": {"inherits": "editor", "level": 80},
    "editor": {"inherits": "viewer", "level": 50},
    "viewer": {"inherits": None, "level": 10},
}

PERMISSIONS = {
    "superadmin": ["*"],
    "admin": ["users.manage", "settings.manage", "apps.manage", "billing.view"],
    "editor": ["apps.edit", "content.edit", "content.create"],
    "viewer": ["apps.view", "content.view", "dashboard.view"],
}


def get_effective_permissions(role: str) -> list[str]:
    perms = set()
    current = role
    while current:
        perms.update(PERMISSIONS.get(current, []))
        current = ROLE_HIERARCHY.get(current, {}).get("inherits")
    return sorted(perms)


def check_permission(role: str, permission: str) -> dict:
    effective = get_effective_permissions(role)
    allowed = "*" in effective or permission in effective
    return {"role": role, "permission": permission, "allowed": allowed,
            "effective_permissions": len(effective)}


def compare_roles(role_a: str, role_b: str) -> dict:
    perms_a = set(get_effective_permissions(role_a))
    perms_b = set(get_effective_permissions(role_b))
    return {"role_a": role_a, "role_b": role_b,
            "shared": sorted(perms_a & perms_b),
            "only_a": sorted(perms_a - perms_b),
            "only_b": sorted(perms_b - perms_a)}
