"""App API Billing Event — track billable API events.

Manages billing events:
- Record billable events with amounts
- Aggregate by period
- Invoice generation data
- Per-installation scoped events
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class BillingEvent:
    """A billable API event."""

    event_id: str
    event_type: str
    amount: float
    currency: str = "USD"
    period: str = ""  # "2024-01"


class AppAPIBillingEvent:
    """Track billable API events."""

    def __init__(self) -> None:
        self._events: dict[str, list[BillingEvent]] = {}

    def record(
        self, installation_id: str, event_id: str, event_type: str,
        amount: float, currency: str = "USD", period: str = "",
    ) -> BillingEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if amount < 0:
            raise ValueError("amount must be non-negative")

        event = BillingEvent(
            event_id=event_id, event_type=event_type,
            amount=amount, currency=currency, period=period,
        )
        self._events.setdefault(installation_id, []).append(event)
        return event

    def total(self, installation_id: str, period: str | None = None) -> float:
        events = self._events.get(installation_id, [])
        if period:
            events = [e for e in events if e.period == period]
        return round(sum(e.amount for e in events), 2)

    def by_type(self, installation_id: str) -> dict[str, float]:
        result: dict[str, float] = {}
        for e in self._events.get(installation_id, []):
            result[e.event_type] = round(result.get(e.event_type, 0) + e.amount, 2)
        return result

    def count(self, installation_id: str) -> int:
        return len(self._events.get(installation_id, []))
