"""App Audit Log — comprehensive action audit trail.

Tracks all user and system actions:
- Record actions with actor, resource, detail
- Query by actor, resource type, or time
- Retention limit
- Per-installation scoped logs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class AuditEntry:
    """An audit log entry."""

    entry_id: str
    actor: str
    action: str  # "create", "update", "delete", "access", "login", "logout"
    resource_type: str  # "user", "app", "webhook", etc.
    resource_id: str
    detail: str = ""
    ip_address: str = ""
    timestamp: float = field(default_factory=time.time)


class AppAuditLog:
    """Comprehensive action audit trail."""

    def __init__(self, max_entries: int = 10000) -> None:
        self._max = max(1, max_entries)
        self._entries: dict[str, list[AuditEntry]] = {}

    def record(
        self, installation_id: str, entry_id: str, actor: str,
        action: str, resource_type: str, resource_id: str,
        detail: str = "", ip_address: str = "",
    ) -> AuditEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not actor:
            raise ValueError("actor is required")
        if action not in ("create", "update", "delete", "access", "login", "logout"):
            raise ValueError(f"Invalid action: {action}")

        entry = AuditEntry(
            entry_id=entry_id, actor=actor, action=action,
            resource_type=resource_type, resource_id=resource_id,
            detail=detail, ip_address=ip_address,
        )
        entries = self._entries.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max:
            self._entries[installation_id] = entries[-self._max:]
        return entry

    def by_actor(self, installation_id: str, actor: str, limit: int = 50) -> list[AuditEntry]:
        entries = self._entries.get(installation_id, [])
        filtered = [e for e in entries if e.actor == actor]
        return list(reversed(filtered[-limit:]))

    def by_resource(self, installation_id: str, resource_type: str, resource_id: str | None = None) -> list[AuditEntry]:
        entries = self._entries.get(installation_id, [])
        filtered = [e for e in entries if e.resource_type == resource_type]
        if resource_id:
            filtered = [e for e in filtered if e.resource_id == resource_id]
        return filtered

    def recent(self, installation_id: str, limit: int = 50) -> list[AuditEntry]:
        entries = self._entries.get(installation_id, [])
        return list(reversed(entries[-limit:]))

    def count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
