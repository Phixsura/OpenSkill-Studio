"""Telemetry Collector — opt-in performance and error telemetry from extensions.

Collects anonymized performance metrics, crash reports, and usage patterns
from extensions with user consent, for developer debugging.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TelemetryEvent:
    extension_id: str
    event_name: str
    value: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class TelemetryCollector:
    """Collects and aggregates opt-in extension telemetry."""

    def __init__(self):
        self._events: dict[str, list[TelemetryEvent]] = defaultdict(list)
        self._opted_in: set[str] = set()  # org_ids that opted in
        self._counters: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def opt_in(self, org_id: str) -> None:
        self._opted_in.add(org_id)

    def opt_out(self, org_id: str) -> None:
        self._opted_in.discard(org_id)

    def is_opted_in(self, org_id: str) -> bool:
        return org_id in self._opted_in

    def record(self, extension_id: str, event_name: str, value: float = 0.0,
               tags: dict[str, str] | None = None, org_id: str = "") -> bool:
        """Record a telemetry event. Rejected if org not opted in."""
        if org_id and not self.is_opted_in(org_id):
            return False
        event = TelemetryEvent(extension_id=extension_id, event_name=event_name,
                                value=value, tags=tags or {})
        self._events[extension_id].append(event)
        self._counters[extension_id][event_name] += 1
        return True

    def increment(self, extension_id: str, counter_name: str, amount: int = 1) -> None:
        """Increment a named counter (always allowed, no PII)."""
        self._counters[extension_id][counter_name] += amount

    def get_counter(self, extension_id: str, counter_name: str) -> int:
        return self._counters.get(extension_id, {}).get(counter_name, 0)

    def get_aggregates(self, extension_id: str, event_name: str) -> dict:
        """Get min/max/avg/count for a specific event metric."""
        events = [e for e in self._events.get(extension_id, [])
                  if e.event_name == event_name]
        if not events:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "sum": 0}
        values = [e.value for e in events]
        return {
            "count": len(values),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(sum(values) / len(values), 2),
            "sum": round(sum(values), 2),
        }

    def get_top_events(self, extension_id: str, limit: int = 10) -> list[tuple[str, int]]:
        """Get most frequent events for an extension."""
        counters = self._counters.get(extension_id, {})
        return sorted(counters.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_dashboard(self, extension_id: str) -> dict:
        """Get telemetry dashboard data."""
        events = self._events.get(extension_id, [])
        counters = self._counters.get(extension_id, {})
        return {
            "extension_id": extension_id,
            "total_events": len(events),
            "unique_event_types": len(set(e.event_name for e in events)),
            "counters": dict(counters),
            "top_events": self.get_top_events(extension_id, 5),
        }
