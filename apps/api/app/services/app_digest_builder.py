"""App Digest Builder — aggregate events into periodic digest summaries.

Builds digest summaries for installed apps:
- Collect events into time-based digests (hourly, daily, weekly)
- Group by category
- Summary statistics (counts, top items)
- Per-installation scoped digests
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class DigestPeriod(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class DigestEvent:
    """An event to include in a digest."""

    event_type: str
    title: str
    category: str = "general"
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


@dataclass
class DigestSummary:
    """A compiled digest summary."""

    digest_id: str
    installation_id: str
    period: DigestPeriod
    start_at: float
    end_at: float
    total_events: int
    by_category: dict[str, int]
    top_event_types: list[tuple[str, int]]
    events: list[DigestEvent]


class AppDigestBuilder:
    """Aggregate events into periodic digest summaries."""

    def __init__(self) -> None:
        # (installation_id) → list[DigestEvent]
        self._events: dict[str, list[DigestEvent]] = {}
        self._digests: dict[tuple[str, str], DigestSummary] = {}

    def add_event(
        self,
        installation_id: str,
        event_type: str,
        title: str,
        category: str = "general",
        metadata: dict | None = None,
        now: float | None = None,
    ) -> DigestEvent:
        """Add an event for future digest inclusion."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not event_type:
            raise ValueError("event_type is required")
        if not title:
            raise ValueError("title is required")

        event = DigestEvent(
            event_type=event_type, title=title,
            category=category, timestamp=now or time.time(),
            metadata=metadata or {},
        )
        self._events.setdefault(installation_id, []).append(event)
        return event

    def build_digest(
        self,
        installation_id: str,
        digest_id: str,
        period: DigestPeriod,
        start_at: float,
        end_at: float,
    ) -> DigestSummary:
        """Build a digest from events in a time range."""
        if not digest_id:
            raise ValueError("digest_id is required")
        if end_at <= start_at:
            raise ValueError("end_at must be after start_at")

        all_events = self._events.get(installation_id, [])
        window_events = [
            e for e in all_events if start_at <= e.timestamp < end_at
        ]

        # Group by category
        by_category: dict[str, int] = {}
        type_counts: dict[str, int] = {}
        for e in window_events:
            by_category[e.category] = by_category.get(e.category, 0) + 1
            type_counts[e.event_type] = type_counts.get(e.event_type, 0) + 1

        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        digest = DigestSummary(
            digest_id=digest_id,
            installation_id=installation_id,
            period=period,
            start_at=start_at,
            end_at=end_at,
            total_events=len(window_events),
            by_category=by_category,
            top_event_types=top_types,
            events=window_events,
        )
        self._digests[(installation_id, digest_id)] = digest
        return digest

    def get_digest(self, installation_id: str, digest_id: str) -> DigestSummary:
        key = (installation_id, digest_id)
        d = self._digests.get(key)
        if d is None:
            raise KeyError(f"Digest {digest_id} not found")
        return d

    def event_count(self, installation_id: str) -> int:
        return len(self._events.get(installation_id, []))
