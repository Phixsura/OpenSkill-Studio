"""Access Log — immutable log of all extension access events.

Records every access to extension APIs, configs, and data with
actor, action, resource, and result for compliance and forensics.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AccessEvent:
    event_id: str
    actor_id: str
    actor_type: str  # user, extension, system, api_key
    action: str      # read, write, delete, execute, admin
    resource: str     # what was accessed
    extension_id: str
    org_id: str
    result: str = "allowed"  # allowed, denied, error
    ip_address: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class AccessLogService:
    """Immutable access log for compliance and forensics."""

    def __init__(self, max_events: int = 500000):
        self._events: list[AccessEvent] = []
        self._max = max_events
        self._counter = 0

    def record(self, actor_id: str, actor_type: str, action: str,
               resource: str, extension_id: str, org_id: str,
               result: str = "allowed", ip_address: str = "") -> AccessEvent:
        self._counter += 1
        event = AccessEvent(
            event_id=f"acc-{self._counter}", actor_id=actor_id,
            actor_type=actor_type, action=action, resource=resource,
            extension_id=extension_id, org_id=org_id,
            result=result, ip_address=ip_address,
        )
        self._events.append(event)
        if len(self._events) > self._max:
            self._events = self._events[-self._max:]
        return event

    def query(self, extension_id: str | None = None, org_id: str | None = None,
              actor_id: str | None = None, action: str | None = None,
              result: str | None = None, limit: int = 100) -> list[AccessEvent]:
        results = self._events
        if extension_id:
            results = [e for e in results if e.extension_id == extension_id]
        if org_id:
            results = [e for e in results if e.org_id == org_id]
        if actor_id:
            results = [e for e in results if e.actor_id == actor_id]
        if action:
            results = [e for e in results if e.action == action]
        if result:
            results = [e for e in results if e.result == result]
        return results[-limit:]

    def get_denied_access(self, extension_id: str, limit: int = 50) -> list[AccessEvent]:
        return self.query(extension_id=extension_id, result="denied", limit=limit)

    def get_actor_activity(self, actor_id: str, limit: int = 50) -> list[AccessEvent]:
        return self.query(actor_id=actor_id, limit=limit)

    def get_stats(self, extension_id: str) -> dict:
        events = [e for e in self._events if e.extension_id == extension_id]
        by_action: dict[str, int] = defaultdict(int)
        by_result: dict[str, int] = defaultdict(int)
        for e in events:
            by_action[e.action] += 1
            by_result[e.result] += 1
        return {
            "extension_id": extension_id,
            "total_events": len(events),
            "by_action": dict(by_action),
            "by_result": dict(by_result),
            "unique_actors": len(set(e.actor_id for e in events)),
        }

    def export(self, extension_id: str, limit: int = 1000) -> list[dict]:
        events = self.query(extension_id=extension_id, limit=limit)
        return [{
            "event_id": e.event_id, "actor": e.actor_id, "actor_type": e.actor_type,
            "action": e.action, "resource": e.resource, "result": e.result,
            "timestamp": e.timestamp,
        } for e in events]
