"""RBAC Engine — Role-Based Access Control with hierarchy and inheritance.

Implements:
- Role hierarchy: admin > editor > viewer (child inherits parent permissions)
- Resource-scoped permissions: (resource, action) pairs
- User-to-role assignment with multiple roles per user
- Permission evaluation with deny-override
- Role inheritance resolution via topological traversal
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Permission:
    resource: str
    action: str  # read, write, delete, admin
    effect: str = "allow"  # allow, deny


@dataclass
class Role:
    role_id: str
    name: str
    permissions: list[Permission] = field(default_factory=list)
    inherits: list[str] = field(default_factory=list)  # parent role IDs


class RbacEngineService:
    def __init__(self):
        self._roles: dict[str, Role] = {}
        self._user_roles: dict[str, set[str]] = {}  # user_id -> role_ids

    def create_role(self, role_id: str, name: str,
                    inherits: list[str] | None = None) -> Role:
        # Validate parents exist
        for parent in (inherits or []):
            if parent not in self._roles:
                raise ValueError(f"Parent role {parent} not found")
        role = Role(role_id=role_id, name=name, inherits=inherits or [])
        self._roles[role_id] = role
        return role

    def add_permission(self, role_id: str, resource: str, action: str,
                       effect: str = "allow") -> bool:
        role = self._roles.get(role_id)
        if not role:
            return False
        role.permissions.append(Permission(resource=resource, action=action, effect=effect))
        return True

    def assign_role(self, user_id: str, role_id: str) -> bool:
        if role_id not in self._roles:
            return False
        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()
        self._user_roles[user_id].add(role_id)
        return True

    def revoke_role(self, user_id: str, role_id: str) -> bool:
        roles = self._user_roles.get(user_id)
        if roles and role_id in roles:
            roles.discard(role_id)
            return True
        return False

    def _resolve_roles(self, role_id: str, visited: set[str] | None = None) -> list[str]:
        """Resolve role hierarchy (BFS upward to parents)."""
        if visited is None:
            visited = set()
        if role_id in visited:
            return []
        visited.add(role_id)
        result = [role_id]
        role = self._roles.get(role_id)
        if role:
            for parent in role.inherits:
                result.extend(self._resolve_roles(parent, visited))
        return result

    def _get_all_permissions(self, user_id: str) -> list[Permission]:
        """Get all permissions for a user, including inherited."""
        user_roles = self._user_roles.get(user_id, set())
        all_role_ids = set()
        for rid in user_roles:
            all_role_ids.update(self._resolve_roles(rid))

        permissions = []
        for rid in all_role_ids:
            role = self._roles.get(rid)
            if role:
                permissions.extend(role.permissions)
        return permissions

    def check(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has permission. Deny overrides allow."""
        permissions = self._get_all_permissions(user_id)

        has_allow = False
        for perm in permissions:
            matches = (perm.resource == resource or perm.resource == "*") and \
                      (perm.action == action or perm.action == "*")
            if matches:
                if perm.effect == "deny":
                    return False  # deny always wins
                has_allow = True

        return has_allow

    def get_user_permissions(self, user_id: str) -> list[dict]:
        perms = self._get_all_permissions(user_id)
        return [{"resource": p.resource, "action": p.action, "effect": p.effect}
                for p in perms]

    def get_user_roles(self, user_id: str) -> list[str]:
        return list(self._user_roles.get(user_id, set()))
