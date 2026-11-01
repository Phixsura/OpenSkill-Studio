"""Permission System — fine-grained permission management for extensions.

Defines a permission model where extensions declare required permissions,
organizations grant/deny them, and the system enforces access control.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class PermissionLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@dataclass
class Permission:
    resource: str          # e.g. "projects", "users", "submissions"
    level: PermissionLevel
    description: str = ""


AVAILABLE_PERMISSIONS: dict[str, Permission] = {
    "projects.read": Permission("projects", PermissionLevel.READ, "Read project data"),
    "projects.write": Permission("projects", PermissionLevel.WRITE, "Create/update projects"),
    "users.read": Permission("users", PermissionLevel.READ, "Read user profiles"),
    "submissions.read": Permission("submissions", PermissionLevel.READ, "Read submissions"),
    "submissions.write": Permission("submissions", PermissionLevel.WRITE, "Create submissions"),
    "webhooks.manage": Permission("webhooks", PermissionLevel.ADMIN, "Manage webhook subscriptions"),
    "analytics.read": Permission("analytics", PermissionLevel.READ, "Read analytics data"),
    "settings.admin": Permission("settings", PermissionLevel.ADMIN, "Manage org settings"),
}


class PermissionGrant:
    """Tracks which permissions are granted to an extension in an org."""

    def __init__(self):
        self._grants: dict[str, dict[str, set[str]]] = {}  # org -> ext -> {perms}

    def grant(self, org_id: str, extension_id: str, permissions: list[str]) -> list[str]:
        """Grant permissions. Returns list of actually granted (valid) permissions."""
        valid = [p for p in permissions if p in AVAILABLE_PERMISSIONS]
        if org_id not in self._grants:
            self._grants[org_id] = {}
        if extension_id not in self._grants[org_id]:
            self._grants[org_id][extension_id] = set()
        self._grants[org_id][extension_id].update(valid)
        return valid

    def revoke(self, org_id: str, extension_id: str, permissions: list[str]) -> None:
        """Revoke specific permissions."""
        if org_id in self._grants and extension_id in self._grants[org_id]:
            self._grants[org_id][extension_id] -= set(permissions)

    def revoke_all(self, org_id: str, extension_id: str) -> None:
        """Revoke all permissions for an extension in an org."""
        if org_id in self._grants:
            self._grants[org_id].pop(extension_id, None)

    def check(self, org_id: str, extension_id: str, permission: str) -> bool:
        """Check if an extension has a specific permission in an org."""
        return permission in self._grants.get(org_id, {}).get(extension_id, set())

    def list_granted(self, org_id: str, extension_id: str) -> list[str]:
        """List all granted permissions for an extension in an org."""
        return sorted(self._grants.get(org_id, {}).get(extension_id, set()))

    def audit(self, org_id: str) -> dict[str, list[str]]:
        """Audit all permission grants for an organization."""
        return {
            ext_id: sorted(perms)
            for ext_id, perms in self._grants.get(org_id, {}).items()
            if perms
        }
