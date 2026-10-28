"""App Changelog Timeline — build a unified timeline from multiple event sources.

Builds a unified chronological timeline:
- Merge events from releases, incidents, deployments
- Filter by time range and event type
- Per-installation scoped timelines
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class TimelineEventType(str, Enum):
    RELEASE = "release"
    INCIDENT = "incident"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"
    CONFIG_CHANGE = "config_change"


@dataclass
class TimelineEvent:
    """A unified timeline event."""

    event_id: str
    event_type: TimelineEventType
    title: str
    description: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


class AppChangelogTimeline:
    """Build unified timelines from multiple event sources."""

    def __init__(self) -> None:
        # installation_id → list[TimelineEvent]
        self._events: dict[str, list[TimelineEvent]] = {}

    def add_event(
        self,
        installation_id: str,
        event_id: str,
        event_type: TimelineEventType,
        title: str,
        description: str = "",
        metadata: dict | None = None,
        now: float | None = None,
    ) -> TimelineEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not event_id:
            raise ValueError("event_id is required")
        if not title:
            raise ValueError("title is required")

        event = TimelineEvent(
            event_id=event_id, event_type=event_type,
            title=title, description=description,
            timestamp=now or time.time(),
            metadata=metadata or {},
        )
        self._events.setdefault(installation_id, []).append(event)
        return event

    def get_timeline(
        self,
        installation_id: str,
        event_type: TimelineEventType | None = None,
        since: float | None = None,
        until: float | None = None,
        limit: int = 50,
    ) -> list[TimelineEvent]:
        """Get timeline events, newest first."""
        events = self._events.get(installation_id, [])
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if since is not None:
            events = [e for e in events if e.timestamp >= since]
        if until is not None:
            events = [e for e in events if e.timestamp <= until]
        return list(reversed(sorted(events, key=lambda e: e.timestamp)))[:limit]

    def count_by_type(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self._events.get(installation_id, []):
            counts[e.event_type.value] = counts.get(e.event_type.value, 0) + 1
        return counts

    def event_count(self, installation_id: str) -> int:
        return len(self._events.get(installation_id, []))
