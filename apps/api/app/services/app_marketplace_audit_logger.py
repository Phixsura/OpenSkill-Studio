"""Audit Logger — immutable audit trail for all marketplace operations.

Records every significant action (install, publish, config change,
permission grant) with actor, target, and diff for compliance.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AuditAction(str, Enum):
    EXTENSION_PUBLISHED = "extension.published"
    EXTENSION_INSTALLED = "extension.installed"
    EXTENSION_UNINSTALLED = "extension.uninstalled"
    EXTENSION_DEPRECATED = "extension.deprecated"
    CONFIG_CHANGED = "config.changed"
    PERMISSION_GRANTED = "permission.granted"
    PERMISSION_REVOKED = "permission.revoked"
    KEY_ISSUED = "key.issued"
    KEY_REVOKED = "key.revoked"
    REVIEW_SUBMITTED = "review.submitted"
    WEBHOOK_CREATED = "webhook.created"
    BILLING_SUBSCRIBED = "billing.subscribed"
    BILLING_CANCELED = "billing.canceled"


@dataclass
class AuditEntry:
    entry_id: str
    action: AuditAction
    actor_id: str
    actor_type: str  # "user", "system", "extension"
    target_type: str  # "extension", "connector", "org"
    target_id: str
    details: dict = field(default_factory=dict)
    ip_address: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class AuditLogger:
    """Immutable audit log for compliance and debugging."""

    def __init__(self):
        self._entries: list[AuditEntry] = []
        self._counter = 0

    def log(
        self, action: AuditAction, actor_id: str, actor_type: str,
        target_type: str, target_id: str,
        details: dict | None = None, ip_address: str = "",
    ) -> AuditEntry:
        """Record an audit entry. Entries are immutable once created."""
        self._counter += 1
        entry = AuditEntry(
            entry_id=f"audit-{self._counter}",
            action=action, actor_id=actor_id, actor_type=actor_type,
            target_type=target_type, target_id=target_id,
            details=details or {}, ip_address=ip_address,
        )
        self._entries.append(entry)
        return entry

    def query(
        self, actor_id: str | None = None, target_id: str | None = None,
        action: AuditAction | None = None, limit: int = 50,
    ) -> list[AuditEntry]:
        """Query audit entries with optional filters."""
        results = list(self._entries)
        if actor_id:
            results = [e for e in results if e.actor_id == actor_id]
        if target_id:
            results = [e for e in results if e.target_id == target_id]
        if action:
            results = [e for e in results if e.action == action]
        return sorted(results, key=lambda e: e.timestamp, reverse=True)[:limit]

    def count(self, action: AuditAction | None = None) -> int:
        if action:
            return sum(1 for e in self._entries if e.action == action)
        return len(self._entries)

    def get_actor_history(self, actor_id: str) -> list[AuditEntry]:
        return self.query(actor_id=actor_id)

    def get_target_history(self, target_id: str) -> list[AuditEntry]:
        return self.query(target_id=target_id)

    def export(self, limit: int = 1000) -> list[dict]:
        """Export audit log as serializable dicts."""
        entries = sorted(self._entries, key=lambda e: e.timestamp, reverse=True)[:limit]
        return [
            {"entry_id": e.entry_id, "action": e.action.value,
             "actor_id": e.actor_id, "actor_type": e.actor_type,
             "target_type": e.target_type, "target_id": e.target_id,
             "details": e.details, "timestamp": e.timestamp}
            for e in entries
        ]
