"""Consumer Billing Meter — track metered usage for billing calculations."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class UsageEvent:
    event_id: str
    metric: str       # "api_calls", "data_transfer_bytes", "compute_seconds"
    quantity: float
    timestamp: datetime
    metadata: dict[str, str] = field(default_factory=dict)

@dataclass
class MeterSummary:
    metric: str
    total: float
    count: int
    first_at: datetime | None = None
    last_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerBillingMeter:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], list[UsageEvent]] = {}  # (inst, consumer) -> events

    def record(self, installation_id: str, consumer_id: str, event: UsageEvent) -> UsageEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if event.quantity < 0:
            raise ValueError("Quantity must be non-negative")
        key = (installation_id, consumer_id)
        if key not in self._events:
            self._events[key] = []
        self._events[key].append(event)
        log.info("billing_event", installation_id=installation_id, consumer_id=consumer_id, metric=event.metric, qty=event.quantity)
        return event

    def summarize(self, installation_id: str, consumer_id: str, metric: str | None = None) -> list[MeterSummary]:
        events = self._events.get((installation_id, consumer_id), [])
        if metric:
            events = [e for e in events if e.metric == metric]
        by_metric: dict[str, list[UsageEvent]] = {}
        for e in events:
            by_metric.setdefault(e.metric, []).append(e)
        result = []
        for m, evts in sorted(by_metric.items()):
            result.append(MeterSummary(
                metric=m, total=sum(e.quantity for e in evts), count=len(evts),
                first_at=min(e.timestamp for e in evts), last_at=max(e.timestamp for e in evts),
            ))
        return result

    def usage_between(self, installation_id: str, consumer_id: str, start: datetime, end: datetime) -> list[UsageEvent]:
        events = self._events.get((installation_id, consumer_id), [])
        return [e for e in events if start <= e.timestamp <= end]

    def total_for_metric(self, installation_id: str, consumer_id: str, metric: str) -> float:
        events = self._events.get((installation_id, consumer_id), [])
        return sum(e.quantity for e in events if e.metric == metric)
