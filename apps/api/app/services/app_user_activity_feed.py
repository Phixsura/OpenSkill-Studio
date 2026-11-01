"""App User Activity Feed — track and display user activity streams.

Manages activity feeds for installed apps:
- Record user actions with metadata
- Query feed with filters
- Activity type categorization
- Per-installation scoped feeds
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ActivityEvent:
    """A user activity event."""

    event_id: str
    user_id: str
    action: str  # e.g. "created", "updated", "deleted", "viewed"
    resource_type: str
    resource_id: str
    description: str = ""
    timestamp: float = field(default_factory=time.time)


class AppUserActivityFeed:
    """Track and display user activity streams."""

    def __init__(self, max_events: int = 5000) -> None:
        self._events: dict[str, list[ActivityEvent]] = {}
        self._max = max(100, max_events)

    def record(
        self,
        installation_id: str,
        event_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        description: str = "",
        now: float | None = None,
    ) -> ActivityEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not user_id:
            raise ValueError("user_id is required")
        if not action:
            raise ValueError("action is required")

        event = ActivityEvent(
            event_id=event_id, user_id=user_id,
            action=action, resource_type=resource_type,
            resource_id=resource_id, description=description,
            timestamp=now or time.time(),
        )
        events = self._events.setdefault(installation_id, [])
        events.append(event)
        if len(events) > self._max:
            self._events[installation_id] = events[-self._max:]
        return event

    def get_feed(
        self,
        installation_id: str,
        user_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        limit: int = 50,
    ) -> list[ActivityEvent]:
        """Get activity feed, newest first."""
        events = self._events.get(installation_id, [])
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if action:
            events = [e for e in events if e.action == action]
        if resource_type:
            events = [e for e in events if e.resource_type == resource_type]
        return list(reversed(events[-limit:]))

    def get_user_summary(self, installation_id: str, user_id: str) -> dict[str, int]:
        """Count actions by type for a user."""
        counts: dict[str, int] = {}
        for e in self._events.get(installation_id, []):
            if e.user_id == user_id:
                counts[e.action] = counts.get(e.action, 0) + 1
        return counts

    def event_count(self, installation_id: str) -> int:
        return len(self._events.get(installation_id, []))
