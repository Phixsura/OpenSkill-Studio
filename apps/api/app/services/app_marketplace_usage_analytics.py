"""Usage Analytics — track and aggregate extension usage metrics.

Collects usage events from extensions, aggregates them into
time-bucketed metrics, and provides insights for developers.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone


class UsageAnalytics:
    """Collects and queries extension usage data."""

    def __init__(self):
        self._events: list[dict] = []
        self._daily_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def record_event(
        self, extension_id: str, event_type: str, org_id: str = "",
        user_id: str = "", metadata: dict | None = None,
    ) -> dict:
        """Record a usage event."""
        now = datetime.now(timezone.utc)
        event = {
            "extension_id": extension_id,
            "event_type": event_type,
            "org_id": org_id,
            "user_id": user_id,
            "metadata": metadata or {},
            "timestamp": now.isoformat(),
        }
        self._events.append(event)
        day_key = now.strftime("%Y-%m-%d")
        bucket = f"{extension_id}:{event_type}"
        self._daily_counts[day_key][bucket] += 1
        return event

    def get_event_count(self, extension_id: str, event_type: str | None = None) -> int:
        """Get total event count for an extension."""
        return sum(
            1 for e in self._events
            if e["extension_id"] == extension_id
            and (event_type is None or e["event_type"] == event_type)
        )

    def get_unique_users(self, extension_id: str) -> int:
        """Get count of unique users for an extension."""
        users = {e["user_id"] for e in self._events
                 if e["extension_id"] == extension_id and e["user_id"]}
        return len(users)

    def get_unique_orgs(self, extension_id: str) -> int:
        """Get count of unique orgs using an extension."""
        orgs = {e["org_id"] for e in self._events
                if e["extension_id"] == extension_id and e["org_id"]}
        return len(orgs)

    def get_top_extensions(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get most used extensions by event count."""
        counts: dict[str, int] = defaultdict(int)
        for e in self._events:
            counts[e["extension_id"]] += 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_daily_breakdown(self, extension_id: str) -> dict[str, int]:
        """Get daily event counts for an extension."""
        result: dict[str, int] = {}
        for day, buckets in self._daily_counts.items():
            total = sum(v for k, v in buckets.items() if k.startswith(f"{extension_id}:"))
            if total:
                result[day] = total
        return result

    def get_summary(self, extension_id: str) -> dict:
        """Get a summary of analytics for an extension."""
        return {
            "extension_id": extension_id,
            "total_events": self.get_event_count(extension_id),
            "unique_users": self.get_unique_users(extension_id),
            "unique_orgs": self.get_unique_orgs(extension_id),
            "event_types": list({
                e["event_type"] for e in self._events
                if e["extension_id"] == extension_id
            }),
        }
