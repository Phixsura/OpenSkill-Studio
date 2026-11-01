"""User role manager — RBAC role assignment and permission checking."""
from __future__ import annotations

ROLES = {
    "viewer": {"level": 0, "permissions": ["read"]},
    "member": {"level": 1, "permissions": ["read", "create"]},
    "editor": {"level": 2, "permissions": ["read", "create", "update"]},
    "admin": {"level": 3, "permissions": ["read", "create", "update", "delete", "manage"]},
    "owner": {"level": 4, "permissions": ["read", "create", "update", "delete", "manage", "billing", "transfer"]},
}


def get_permissions(role: str) -> list[str]:
    return ROLES.get(role, ROLES["viewer"])["permissions"]


def can_perform(role: str, action: str) -> bool:
    return action in get_permissions(role)


def can_assign_role(assigner_role: str, target_role: str) -> bool:
    assigner = ROLES.get(assigner_role, {"level": 0})
    target = ROLES.get(target_role, {"level": 0})
    return assigner["level"] > target["level"]


def list_roles() -> list[dict]:
    return [{"role": k, "level": v["level"], "permissions": v["permissions"],
             "permission_count": len(v["permissions"])} for k, v in ROLES.items()]
