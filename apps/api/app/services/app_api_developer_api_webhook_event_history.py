"""App API Developer Webhook Event History — comprehensive event history view."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class EventHistoryEntry:
    event_id: str
    event_type: str
    destination: str
    status: str  # "delivered", "failed", "retrying", "dead_letter"
    latency_ms: float
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperAPIWebhookEventHistory:
    def __init__(self, max_entries: int = 10000) -> None:
        self._max = max(1, max_entries)
        self._history: dict[str, list[EventHistoryEntry]] = {}

    def record(self, installation_id: str, event_id: str, event_type: str, destination: str, status: str, latency_ms: float) -> EventHistoryEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if status not in ("delivered", "failed", "retrying", "dead_letter"): raise ValueError("invalid status")
        e = EventHistoryEntry(event_id=event_id, event_type=event_type, destination=destination, status=status, latency_ms=latency_ms)
        entries = self._history.setdefault(installation_id, [])
        entries.append(e)
        if len(entries) > self._max: self._history[installation_id] = entries[-self._max:]
        return e

    def recent(self, installation_id: str, limit: int = 50) -> list[EventHistoryEntry]:
        return list(reversed(self._history.get(installation_id, [])[-limit:]))

    def by_status(self, installation_id: str, status: str) -> list[EventHistoryEntry]:
        return [e for e in self._history.get(installation_id, []) if e.status == status]

    def count(self, installation_id: str) -> int:
        return len(self._history.get(installation_id, []))
