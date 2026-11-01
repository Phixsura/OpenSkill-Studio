"""App Permission Policy — manage fine-grained permissions.

Manages permission policies:
- Define permissions by resource and action
- Assign permissions to roles
- Check authorization
- Per-installation scoped policies
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Permission:
    """A permission definition."""

    resource: str  # "app", "webhook", "settings"
    action: str  # "read", "write", "delete", "admin"

    @property
    def key(self) -> str:
        return f"{self.resource}:{self.action}"


@dataclass
class Role:
    """A role with permissions."""

    role_id: str
    name: str
    permissions: list[Permission] = field(default_factory=list)

    def has_permission(self, resource: str, action: str) -> bool:
        return any(
            p.resource == resource and (p.action == action or p.action == "admin")
            for p in self.permissions
        )


class AppPermissionPolicy:
    """Manage fine-grained permissions."""

    def __init__(self) -> None:
        self._roles: dict[tuple[str, str], Role] = {}
        self._user_roles: dict[tuple[str, str], list[str]] = {}  # (inst, user) → role_ids

    def create_role(
        self, installation_id: str, role_id: str, name: str,
        permissions: list[dict],
    ) -> Role:
        if not installation_id:
            raise ValueError("installation_id is required")

        perm_objs = [Permission(resource=p["resource"], action=p["action"]) for p in permissions]
        role = Role(role_id=role_id, name=name, permissions=perm_objs)
        self._roles[(installation_id, role_id)] = role
        return role

    def assign_role(self, installation_id: str, user_id: str, role_id: str) -> None:
        if (installation_id, role_id) not in self._roles:
            raise KeyError(f"Role {role_id} not found")
        roles = self._user_roles.setdefault((installation_id, user_id), [])
        if role_id not in roles:
            roles.append(role_id)

    def check(self, installation_id: str, user_id: str, resource: str, action: str) -> bool:
        """Check if user has permission via any assigned role."""
        role_ids = self._user_roles.get((installation_id, user_id), [])
        for rid in role_ids:
            role = self._roles.get((installation_id, rid))
            if role and role.has_permission(resource, action):
                return True
        return False

    def user_permissions(self, installation_id: str, user_id: str) -> list[str]:
        """All permission keys for a user."""
        perms: set[str] = set()
        role_ids = self._user_roles.get((installation_id, user_id), [])
        for rid in role_ids:
            role = self._roles.get((installation_id, rid))
            if role:
                for p in role.permissions:
                    perms.add(p.key)
        return sorted(perms)

    def list_roles(self, installation_id: str) -> list[Role]:
        return [r for (inst, _), r in self._roles.items() if inst == installation_id]
