"""App API Webhook Event Log — immutable log of webhook events emitted."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class WebhookEventLog:
    event_id: str
    event_type: str
    destination_count: int
    payload_size: int
    emitted_at: float = field(default_factory=time.time)

class AppAPIWebhookEventLog:
    def __init__(self, max_entries: int = 10000) -> None:
        self._max = max(1, max_entries)
        self._logs: dict[str, list[WebhookEventLog]] = {}

    def log_event(self, installation_id: str, event_id: str, event_type: str, destination_count: int, payload_size: int) -> WebhookEventLog:
        if not installation_id: raise ValueError("installation_id is required")
        entry = WebhookEventLog(event_id=event_id, event_type=event_type, destination_count=destination_count, payload_size=payload_size)
        entries = self._logs.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max: self._logs[installation_id] = entries[-self._max:]
        return entry

    def recent(self, installation_id: str, limit: int = 50) -> list[WebhookEventLog]:
        return list(reversed(self._logs.get(installation_id, [])[-limit:]))

    def by_type(self, installation_id: str, event_type: str) -> list[WebhookEventLog]:
        return [e for e in self._logs.get(installation_id, []) if e.event_type == event_type]

    def count(self, installation_id: str) -> int:
        return len(self._logs.get(installation_id, []))
