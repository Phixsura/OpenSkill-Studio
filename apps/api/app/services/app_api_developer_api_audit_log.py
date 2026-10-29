"""App API Developer Audit Log — immutable audit trail for platform actions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class AuditEntry:
    entry_id: str
    actor: str
    action: str  # "create", "update", "delete", "access", "revoke"
    resource_type: str
    resource_id: str
    timestamp: float = field(default_factory=time.time)
    details: dict[str, str] = field(default_factory=dict)
    ip_address: str = ""

class AppAPIDeveloperAPIAuditLog:
    def __init__(self, max_entries: int = 10000) -> None:
        self._max = max(1, max_entries)
        self._entries: dict[str, list[AuditEntry]] = {}

    def log(self, installation_id: str, entry_id: str, actor: str, action: str, resource_type: str, resource_id: str, details: dict[str, str] | None = None, ip_address: str = "") -> AuditEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if action not in ("create", "update", "delete", "access", "revoke"): raise ValueError("invalid action")
        e = AuditEntry(entry_id=entry_id, actor=actor, action=action, resource_type=resource_type, resource_id=resource_id, details=details or {}, ip_address=ip_address)
        entries = self._entries.setdefault(installation_id, [])
        entries.append(e)
        if len(entries) > self._max: self._entries[installation_id] = entries[-self._max:]
        return e

    def query(self, installation_id: str, actor: str | None = None, action: str | None = None, resource_type: str | None = None, limit: int = 50) -> list[AuditEntry]:
        entries = self._entries.get(installation_id, [])
        if actor: entries = [e for e in entries if e.actor == actor]
        if action: entries = [e for e in entries if e.action == action]
        if resource_type: entries = [e for e in entries if e.resource_type == resource_type]
        return list(reversed(entries[-limit:]))

    def count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
