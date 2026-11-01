"""App API Developer Webhook Delivery Timeline — chronological delivery view."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryTimelineEntry:
    delivery_id: str
    event_type: str
    destination: str
    status: str  # "success", "failure", "timeout", "retry"
    latency_ms: float
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperAPIWebhookDeliveryTimeline:
    def __init__(self, max_entries: int = 5000) -> None:
        self._max = max(1, max_entries)
        self._entries: dict[str, list[DeliveryTimelineEntry]] = {}

    def record(self, installation_id: str, delivery_id: str, event_type: str, destination: str, status: str, latency_ms: float) -> DeliveryTimelineEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if status not in ("success", "failure", "timeout", "retry"): raise ValueError("invalid status")
        e = DeliveryTimelineEntry(delivery_id=delivery_id, event_type=event_type, destination=destination, status=status, latency_ms=latency_ms)
        entries = self._entries.setdefault(installation_id, [])
        entries.append(e)
        if len(entries) > self._max: self._entries[installation_id] = entries[-self._max:]
        return e

    def recent(self, installation_id: str, limit: int = 50) -> list[DeliveryTimelineEntry]:
        return list(reversed(self._entries.get(installation_id, [])[-limit:]))

    def failures(self, installation_id: str) -> list[DeliveryTimelineEntry]:
        return [e for e in self._entries.get(installation_id, []) if e.status in ("failure", "timeout")]

    def count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
