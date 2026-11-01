"""App Permission Matrix — role-based permission management for installed apps.

Manages granular permissions for app resources:
- Define resources and actions (e.g. "projects:read", "users:delete")
- Role-based permission assignment
- Permission checking with role hierarchy
- Wildcard support (resource:* grants all actions)
- Per-installation scoped permission sets
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Permission:
    """A single permission entry."""

    resource: str  # e.g. "projects", "users", "settings"
    action: str    # e.g. "read", "write", "delete", "*"


@dataclass
class Role:
    """A role with assigned permissions."""

    role_id: str
    name: str
    permissions: list[Permission] = field(default_factory=list)
    inherits_from: str | None = None  # role_id to inherit from


@dataclass
class PermissionCheck:
    """Result of checking a permission."""

    allowed: bool
    role_id: str
    resource: str
    action: str
    reason: str  # "direct", "wildcard", "inherited", "denied"


class AppPermissionMatrix:
    """Role-based permission management for installed apps."""

    def __init__(self) -> None:
        # (installation_id, role_id) → Role
        self._roles: dict[tuple[str, str], Role] = {}

    def create_role(
        self,
        installation_id: str,
        role_id: str,
        name: str,
        inherits_from: str | None = None,
    ) -> Role:
        """Create a new role."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not role_id:
            raise ValueError("role_id is required")
        if not name:
            raise ValueError("name is required")

        key = (installation_id, role_id)
        if key in self._roles:
            raise ValueError(f"Role {role_id} already exists")

        # Validate inheritance target exists
        if inherits_from:
            parent_key = (installation_id, inherits_from)
            if parent_key not in self._roles:
                raise KeyError(f"Parent role {inherits_from} not found")

        role = Role(role_id=role_id, name=name, inherits_from=inherits_from)
        self._roles[key] = role
        return role

    def grant_permission(
        self,
        installation_id: str,
        role_id: str,
        resource: str,
        action: str,
    ) -> Permission:
        """Grant a permission to a role."""
        role = self._get_role(installation_id, role_id)
        if not resource:
            raise ValueError("resource is required")
        if not action:
            raise ValueError("action is required")

        # Avoid duplicates
        for p in role.permissions:
            if p.resource == resource and p.action == action:
                return p

        perm = Permission(resource=resource, action=action)
        role.permissions.append(perm)
        return perm

    def revoke_permission(
        self,
        installation_id: str,
        role_id: str,
        resource: str,
        action: str,
    ) -> bool:
        """Revoke a permission from a role. Returns True if found."""
        role = self._get_role(installation_id, role_id)
        before = len(role.permissions)
        role.permissions = [
            p for p in role.permissions
            if not (p.resource == resource and p.action == action)
        ]
        return len(role.permissions) < before

    def check_permission(
        self,
        installation_id: str,
        role_id: str,
        resource: str,
        action: str,
    ) -> PermissionCheck:
        """Check if a role has a specific permission."""
        return self._check_recursive(
            installation_id, role_id, resource, action, visited=set()
        )

    def get_effective_permissions(
        self, installation_id: str, role_id: str
    ) -> list[Permission]:
        """Get all permissions including inherited ones."""
        perms: list[Permission] = []
        seen: set[tuple[str, str]] = set()
        self._collect_permissions(installation_id, role_id, perms, seen, visited=set())
        return perms

    def list_roles(self, installation_id: str) -> list[Role]:
        return [
            role for (inst, _), role in self._roles.items()
            if inst == installation_id
        ]

    def get_role(self, installation_id: str, role_id: str) -> Role:
        return self._get_role(installation_id, role_id)

    def _check_recursive(
        self,
        installation_id: str,
        role_id: str,
        resource: str,
        action: str,
        visited: set[str],
    ) -> PermissionCheck:
        if role_id in visited:
            return PermissionCheck(
                allowed=False, role_id=role_id,
                resource=resource, action=action, reason="denied",
            )
        visited.add(role_id)

        role = self._roles.get((installation_id, role_id))
        if role is None:
            return PermissionCheck(
                allowed=False, role_id=role_id,
                resource=resource, action=action, reason="denied",
            )

        # Direct match
        for p in role.permissions:
            if p.resource == resource and p.action == action:
                return PermissionCheck(
                    allowed=True, role_id=role_id,
                    resource=resource, action=action, reason="direct",
                )

        # Wildcard match
        for p in role.permissions:
            if p.resource == resource and p.action == "*":
                return PermissionCheck(
                    allowed=True, role_id=role_id,
                    resource=resource, action=action, reason="wildcard",
                )

        # Inheritance
        if role.inherits_from:
            result = self._check_recursive(
                installation_id, role.inherits_from,
                resource, action, visited,
            )
            if result.allowed:
                return PermissionCheck(
                    allowed=True, role_id=role_id,
                    resource=resource, action=action, reason="inherited",
                )

        return PermissionCheck(
            allowed=False, role_id=role_id,
            resource=resource, action=action, reason="denied",
        )

    def _collect_permissions(
        self,
        installation_id: str,
        role_id: str,
        perms: list[Permission],
        seen: set[tuple[str, str]],
        visited: set[str],
    ) -> None:
        if role_id in visited:
            return
        visited.add(role_id)

        role = self._roles.get((installation_id, role_id))
        if role is None:
            return

        for p in role.permissions:
            key = (p.resource, p.action)
            if key not in seen:
                seen.add(key)
                perms.append(p)

        if role.inherits_from:
            self._collect_permissions(
                installation_id, role.inherits_from, perms, seen, visited,
            )

    def _get_role(self, installation_id: str, role_id: str) -> Role:
        key = (installation_id, role_id)
        role = self._roles.get(key)
        if role is None:
            raise KeyError(f"Role {role_id} not found")
        return role
