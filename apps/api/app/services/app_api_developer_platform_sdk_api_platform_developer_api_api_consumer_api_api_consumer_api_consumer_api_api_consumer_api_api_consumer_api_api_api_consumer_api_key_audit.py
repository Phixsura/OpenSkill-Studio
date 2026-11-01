"""Consumer API Key Audit — audit trail for API key lifecycle events."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class KeyAuditEvent:
    event_id: str
    key_id: str
    consumer_id: str
    action: str  # "created", "rotated", "revoked", "scopes_changed", "ip_binding_changed"
    actor_id: str
    details: dict[str, str] = field(default_factory=dict)
    ip_address: str = ""
    timestamp: datetime | None = None

VALID_ACTIONS = {"created", "rotated", "revoked", "scopes_changed", "ip_binding_changed", "label_changed", "suspended", "reactivated"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiKeyAudit:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], list[KeyAuditEvent]] = {}  # (inst, consumer)

    def record(self, installation_id: str, event: KeyAuditEvent) -> KeyAuditEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if event.action not in VALID_ACTIONS:
            raise ValueError(f"Invalid action: {event.action}")
        event.timestamp = event.timestamp or datetime.utcnow()
        key = (installation_id, event.consumer_id)
        if key not in self._events:
            self._events[key] = []
        self._events[key].append(event)
        log.info("key_audit", installation_id=installation_id, consumer=event.consumer_id, key=event.key_id, action=event.action)
        return event

    def get_key_history(self, installation_id: str, consumer_id: str, key_id: str) -> list[KeyAuditEvent]:
        events = self._events.get((installation_id, consumer_id), [])
        return [e for e in events if e.key_id == key_id]

    def get_consumer_history(self, installation_id: str, consumer_id: str, action: str | None = None, limit: int = 50) -> list[KeyAuditEvent]:
        events = self._events.get((installation_id, consumer_id), [])
        if action:
            events = [e for e in events if e.action == action]
        return list(reversed(events[-limit:]))

    def count_by_action(self, installation_id: str, consumer_id: str) -> dict[str, int]:
        events = self._events.get((installation_id, consumer_id), [])
        counts: dict[str, int] = {}
        for e in events:
            counts[e.action] = counts.get(e.action, 0) + 1
        return counts
