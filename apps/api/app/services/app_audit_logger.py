"""App Audit Logger — structured audit trail for app actions.

Records structured audit events for installed apps:
- Action tracking with actor, resource, and details
- Severity levels: info, warning, critical
- Time-range queries
- Per-installation scoped logs
- Immutable append-only design
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AuditEvent:
    """An immutable audit log entry."""

    event_id: str
    installation_id: str
    actor: str          # user_id or system identifier
    action: str         # e.g. "key.created", "config.updated", "user.deleted"
    resource_type: str  # e.g. "api_key", "config", "user"
    resource_id: str
    severity: AuditSeverity = AuditSeverity.INFO
    details: str = ""
    ip_address: str = ""
    timestamp: float = field(default_factory=time.time)


class AppAuditLogger:
    """Structured audit trail for app actions."""

    def __init__(self, max_entries: int = 10000) -> None:
        self._events: list[AuditEvent] = []
        self._max_entries = max(100, max_entries)

    def record(
        self,
        installation_id: str,
        event_id: str,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        severity: AuditSeverity = AuditSeverity.INFO,
        details: str = "",
        ip_address: str = "",
        now: float | None = None,
    ) -> AuditEvent:
        """Record an audit event."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not event_id:
            raise ValueError("event_id is required")
        if not actor:
            raise ValueError("actor is required")
        if not action:
            raise ValueError("action is required")

        event = AuditEvent(
            event_id=event_id,
            installation_id=installation_id,
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            severity=severity,
            details=details,
            ip_address=ip_address,
            timestamp=now or time.time(),
        )

        self._events.append(event)
        # Trim to max
        if len(self._events) > self._max_entries:
            self._events = self._events[-self._max_entries:]

        return event

    def query(
        self,
        installation_id: str,
        actor: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        severity: AuditSeverity | None = None,
        since: float | None = None,
        until: float | None = None,
        limit: int = 50,
    ) -> list[AuditEvent]:
        """Query audit events with filters. Returns newest first."""
        if not installation_id:
            raise ValueError("installation_id is required")

        results = [e for e in self._events if e.installation_id == installation_id]

        if actor:
            results = [e for e in results if e.actor == actor]
        if action:
            results = [e for e in results if e.action == action]
        if resource_type:
            results = [e for e in results if e.resource_type == resource_type]
        if severity:
            results = [e for e in results if e.severity == severity]
        if since is not None:
            results = [e for e in results if e.timestamp >= since]
        if until is not None:
            results = [e for e in results if e.timestamp <= until]

        return list(reversed(results[-limit:]))

    def count(self, installation_id: str) -> int:
        """Count total events for an installation."""
        return sum(1 for e in self._events if e.installation_id == installation_id)

    def count_by_severity(self, installation_id: str) -> dict[str, int]:
        """Count events grouped by severity."""
        counts = {s.value: 0 for s in AuditSeverity}
        for e in self._events:
            if e.installation_id == installation_id:
                counts[e.severity.value] += 1
        return counts

    def get_event(self, installation_id: str, event_id: str) -> AuditEvent:
        """Get a specific event by ID."""
        for e in self._events:
            if e.installation_id == installation_id and e.event_id == event_id:
                return e
        raise KeyError(f"Event {event_id} not found")
