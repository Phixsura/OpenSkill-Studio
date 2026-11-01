"""API Audit Trail — immutable audit log for security-sensitive actions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class AuditEvent:
    event_id: str
    actor_id: str
    actor_type: str  # "consumer", "admin", "system", "api_key"
    action: str  # "key.create", "key.revoke", "scope.change", "config.update", etc.
    resource_type: str
    resource_id: str
    details: dict[str, str] = field(default_factory=dict)
    ip_address: str = ""
    timestamp: float = field(default_factory=time.time)

VALID_ACTOR_TYPES = {"consumer", "admin", "system", "api_key"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAuditTrail:
    def __init__(self) -> None:
        self._events: dict[str, list[AuditEvent]] = {}

    def record(self, installation_id: str, event: AuditEvent) -> AuditEvent:
        if not installation_id: raise ValueError("installation_id is required")
        if event.actor_type not in VALID_ACTOR_TYPES: raise ValueError(f"Invalid actor_type: {event.actor_type}")
        # Immutable — no modification after recording
        self._events.setdefault(installation_id, []).append(event)
        return event

    def query(self, installation_id: str, actor_id: str | None = None, action: str | None = None, resource_type: str | None = None, since: float = 0, limit: int = 100) -> list[AuditEvent]:
        events = self._events.get(installation_id, [])
        if actor_id: events = [e for e in events if e.actor_id == actor_id]
        if action: events = [e for e in events if e.action == action]
        if resource_type: events = [e for e in events if e.resource_type == resource_type]
        if since > 0: events = [e for e in events if e.timestamp >= since]
        return list(reversed(events[-limit:]))

    def count(self, installation_id: str) -> int:
        return len(self._events.get(installation_id, []))

    def actions_by_actor(self, installation_id: str, actor_id: str) -> dict[str, int]:
        events = [e for e in self._events.get(installation_id, []) if e.actor_id == actor_id]
        counts: dict[str, int] = {}
        for e in events: counts[e.action] = counts.get(e.action, 0) + 1
        return counts

    def recent_security_events(self, installation_id: str, limit: int = 20) -> list[AuditEvent]:
        security_actions = {"key.create", "key.revoke", "scope.change", "config.update", "access.deny", "token.issue", "token.revoke"}
        events = [e for e in self._events.get(installation_id, []) if e.action in security_actions]
        return list(reversed(events[-limit:]))
