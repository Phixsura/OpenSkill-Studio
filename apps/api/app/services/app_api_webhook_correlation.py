"""App API Webhook Correlation — correlate webhook events with responses."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class CorrelationEntry:
    correlation_id: str
    event_type: str
    destination: str
    sent_at: float = field(default_factory=time.time)
    response_at: float | None = None
    status_code: int | None = None

    @property
    def round_trip_ms(self) -> float | None:
        if self.response_at is None: return None
        return round((self.response_at - self.sent_at) * 1000, 1)

class AppAPIWebhookCorrelation:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], CorrelationEntry] = {}

    def start(self, installation_id: str, correlation_id: str, event_type: str, destination: str) -> CorrelationEntry:
        if not installation_id: raise ValueError("installation_id is required")
        e = CorrelationEntry(correlation_id=correlation_id, event_type=event_type, destination=destination)
        self._entries[(installation_id, correlation_id)] = e
        return e

    def complete(self, installation_id: str, correlation_id: str, status_code: int) -> CorrelationEntry:
        e = self._get(installation_id, correlation_id)
        e.response_at = time.time()
        e.status_code = status_code
        return e

    def pending(self, installation_id: str) -> list[CorrelationEntry]:
        return [e for (inst, _), e in self._entries.items() if inst == installation_id and e.response_at is None]

    def list_entries(self, installation_id: str) -> list[CorrelationEntry]:
        return [e for (inst, _), e in self._entries.items() if inst == installation_id]

    def _get(self, installation_id: str, correlation_id: str) -> CorrelationEntry:
        e = self._entries.get((installation_id, correlation_id))
        if e is None: raise KeyError(f"Correlation {correlation_id} not found")
        return e
