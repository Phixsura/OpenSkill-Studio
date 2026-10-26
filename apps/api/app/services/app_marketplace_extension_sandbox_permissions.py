"""Sandbox Permissions — capability-based permission system for extension sandboxes.

Extensions declare required permissions, users grant/deny them, and the
sandbox enforces them at runtime with least-privilege defaults.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from enum import Enum


class Permission(str, Enum):
    FILE_READ = "file:read"
    FILE_WRITE = "file:write"
    NETWORK_OUTBOUND = "network:outbound"
    NETWORK_INBOUND = "network:inbound"
    CLIPBOARD_READ = "clipboard:read"
    CLIPBOARD_WRITE = "clipboard:write"
    NOTIFICATION = "notification:send"
    CAMERA = "camera:access"
    MICROPHONE = "microphone:access"
    GEOLOCATION = "geolocation:access"
    STORAGE_LOCAL = "storage:local"
    STORAGE_CLOUD = "storage:cloud"
    IPC_SEND = "ipc:send"
    IPC_RECEIVE = "ipc:receive"
    EXEC_SUBPROCESS = "exec:subprocess"


class GrantStatus(str, Enum):
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"


DANGEROUS_PERMISSIONS = {
    Permission.FILE_WRITE, Permission.NETWORK_INBOUND,
    Permission.EXEC_SUBPROCESS, Permission.CAMERA,
    Permission.MICROPHONE,
}


@dataclass
class PermissionGrant:
    grant_id: str
    extension_id: str
    user_id: str
    permission: Permission
    status: GrantStatus = GrantStatus.PENDING
    reason: str = ""


class SandboxPermissionService:
    """Manages capability-based permissions for extension sandboxes."""

    def __init__(self):
        self._declarations: dict[str, set[Permission]] = {}
        self._grants: dict[str, PermissionGrant] = {}
        self._grant_index: dict[tuple[str, str, Permission], str] = {}

    def declare(self, extension_id: str, permissions: list[Permission],
                reasons: dict[Permission, str] | None = None) -> dict:
        self._declarations[extension_id] = set(permissions)
        dangerous = [p for p in permissions if p in DANGEROUS_PERMISSIONS]
        return {
            "extension_id": extension_id,
            "declared": [p.value for p in permissions],
            "dangerous": [p.value for p in dangerous],
            "requires_review": len(dangerous) > 0,
        }

    def request_grant(self, extension_id: str, user_id: str,
                      permission: Permission) -> PermissionGrant:
        declared = self._declarations.get(extension_id, set())
        if permission not in declared:
            raise ValueError(f"Permission not declared: {permission.value}")

        key = (extension_id, user_id, permission)
        if key in self._grant_index:
            return self._grants[self._grant_index[key]]

        grant_id = f"pg_{secrets.token_urlsafe(10)}"
        grant = PermissionGrant(
            grant_id=grant_id, extension_id=extension_id,
            user_id=user_id, permission=permission,
        )
        self._grants[grant_id] = grant
        self._grant_index[key] = grant_id
        return grant

    def approve(self, grant_id: str, approver_user_id: str = "") -> bool:
        grant = self._grants.get(grant_id)
        if not grant or grant.status != GrantStatus.PENDING:
            return False
        if approver_user_id and grant.user_id != approver_user_id:
            raise PermissionError("Only the target user may approve this grant")
        grant.status = GrantStatus.GRANTED
        return True

    def deny(self, grant_id: str, reason: str = "", denier_user_id: str = "") -> bool:
        grant = self._grants.get(grant_id)
        if not grant or grant.status != GrantStatus.PENDING:
            return False
        if denier_user_id and grant.user_id != denier_user_id:
            raise PermissionError("Only the target user may deny this grant")
        grant.status = GrantStatus.DENIED
        grant.reason = reason
        return True

    def revoke(self, grant_id: str) -> bool:
        grant = self._grants.get(grant_id)
        if grant and grant.status == GrantStatus.GRANTED:
            grant.status = GrantStatus.REVOKED
            return True
        return False

    def check(self, extension_id: str, user_id: str,
              permission: Permission) -> bool:
        key = (extension_id, user_id, permission)
        grant_id = self._grant_index.get(key)
        if not grant_id:
            return False
        grant = self._grants[grant_id]
        return grant.status == GrantStatus.GRANTED

    def get_user_grants(self, extension_id: str, user_id: str) -> list[PermissionGrant]:
        return [g for g in self._grants.values()
                if g.extension_id == extension_id and g.user_id == user_id]

    def get_summary(self, extension_id: str) -> dict:
        declared = self._declarations.get(extension_id, set())
        grants = [g for g in self._grants.values() if g.extension_id == extension_id]
        return {
            "declared": len(declared),
            "granted": sum(1 for g in grants if g.status == GrantStatus.GRANTED),
            "denied": sum(1 for g in grants if g.status == GrantStatus.DENIED),
            "pending": sum(1 for g in grants if g.status == GrantStatus.PENDING),
        }
