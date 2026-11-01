"""Consumer API Audit Trail — immutable log of all consumer API actions."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class AuditEvent:
    event_id: str
    consumer_id: str
    actor_id: str
    action: str  # "api_key.created", "webhook.updated", "settings.changed", etc.
    resource_type: str
    resource_id: str
    details: dict[str, str] = field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""
    timestamp: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiAuditTrail:
    def __init__(self, max_events: int = 100000) -> None:
        self._events: dict[tuple[str, str], list[AuditEvent]] = {}  # (inst, consumer)
        self._max = max_events

    def record(self, installation_id: str, event: AuditEvent) -> AuditEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not event.action:
            raise ValueError("action is required")
        event.timestamp = event.timestamp or datetime.utcnow()
        key = (installation_id, event.consumer_id)
        if key not in self._events:
            self._events[key] = []
        self._events[key].append(event)
        if len(self._events[key]) > self._max:
            self._events[key] = self._events[key][-self._max:]
        log.info("audit_recorded", installation_id=installation_id, consumer_id=event.consumer_id, action=event.action)
        return event

    def query(self, installation_id: str, consumer_id: str, action: str | None = None, actor_id: str | None = None, resource_type: str | None = None, limit: int = 50) -> list[AuditEvent]:
        events = self._events.get((installation_id, consumer_id), [])
        if action:
            events = [e for e in events if e.action == action]
        if actor_id:
            events = [e for e in events if e.actor_id == actor_id]
        if resource_type:
            events = [e for e in events if e.resource_type == resource_type]
        return list(reversed(events[-limit:]))

    def count_by_action(self, installation_id: str, consumer_id: str) -> dict[str, int]:
        events = self._events.get((installation_id, consumer_id), [])
        counts: dict[str, int] = {}
        for e in events:
            counts[e.action] = counts.get(e.action, 0) + 1
        return counts

    def count_by_actor(self, installation_id: str, consumer_id: str) -> dict[str, int]:
        events = self._events.get((installation_id, consumer_id), [])
        counts: dict[str, int] = {}
        for e in events:
            counts[e.actor_id] = counts.get(e.actor_id, 0) + 1
        return counts
