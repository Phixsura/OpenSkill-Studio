"""App API Developer Webhook Correlation Tracker — correlate related webhook events."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class CorrelatedEvent:
    event_id: str
    correlation_id: str
    event_type: str
    timestamp: float = field(default_factory=time.time)
    sequence: int = 0

@dataclass
class CorrelationChain:
    correlation_id: str
    events: list[CorrelatedEvent] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        if len(self.events) < 2: return 0.0
        return round((self.events[-1].timestamp - self.events[0].timestamp) * 1000, 1)

    @property
    def event_count(self) -> int:
        return len(self.events)

class AppAPIDeveloperAPIApiWebhookCorrelationTracker:
    def __init__(self) -> None:
        self._chains: dict[tuple[str, str], CorrelationChain] = {}

    def track(self, installation_id: str, correlation_id: str, event_id: str, event_type: str) -> CorrelationChain:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, correlation_id)
        if key not in self._chains:
            self._chains[key] = CorrelationChain(correlation_id=correlation_id)
        chain = self._chains[key]
        seq = len(chain.events)
        chain.events.append(CorrelatedEvent(event_id=event_id, correlation_id=correlation_id, event_type=event_type, sequence=seq))
        return chain

    def get_chain(self, installation_id: str, correlation_id: str) -> CorrelationChain:
        key = (installation_id, correlation_id)
        c = self._chains.get(key)
        if c is None: raise KeyError(f"Chain {correlation_id} not found")
        return c

    def long_chains(self, installation_id: str, min_events: int = 5) -> list[CorrelationChain]:
        return [c for (inst, _), c in self._chains.items() if inst == installation_id and c.event_count >= min_events]

    def total_chains(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._chains if inst == installation_id)
