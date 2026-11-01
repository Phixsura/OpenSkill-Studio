"""Extension Activity Feed — aggregated activity stream for extensions.

Collects install/uninstall/review/deploy/update events into a unified
feed with filtering, pagination, and actor grouping.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ActivityEvent:
    event_id: str
    extension_id: str
    event_type: str  # install, uninstall, review, deploy, update, publish
    actor: str
    message: str
    metadata: dict = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class ExtensionActivityFeedService:
    """Unified activity feed across extension lifecycle events."""

    MAX_EVENTS = 5000

    def __init__(self):
        self._events: list[ActivityEvent] = []

    def record(self, extension_id: str, event_type: str, actor: str,
               message: str, metadata: dict | None = None) -> ActivityEvent:
        event = ActivityEvent(
            event_id=f"act_{secrets.token_urlsafe(8)}",
            extension_id=extension_id, event_type=event_type,
            actor=actor, message=message, metadata=metadata or {},
        )
        self._events.append(event)
        if len(self._events) > self.MAX_EVENTS:
            self._events = self._events[-self.MAX_EVENTS:]
        return event

    def get_feed(self, extension_id: str | None = None,
                 event_type: str | None = None,
                 actor: str | None = None,
                 limit: int = 50) -> list[ActivityEvent]:
        events = self._events
        if extension_id:
            events = [e for e in events if e.extension_id == extension_id]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if actor:
            events = [e for e in events if e.actor == actor]
        return events[-limit:]

    def get_actor_activity(self, actor: str, limit: int = 20) -> list[ActivityEvent]:
        return [e for e in self._events if e.actor == actor][-limit:]

    def get_recent_types(self, extension_id: str) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for e in self._events:
            if e.extension_id == extension_id:
                counts[e.event_type] += 1
        return dict(counts)

    def get_active_extensions(self, limit: int = 10) -> list[dict]:
        counts: dict[str, int] = defaultdict(int)
        for e in self._events:
            counts[e.extension_id] += 1
        sorted_exts = sorted(counts.items(), key=lambda x: -x[1])
        return [{"extension_id": eid, "events": n} for eid, n in sorted_exts[:limit]]
