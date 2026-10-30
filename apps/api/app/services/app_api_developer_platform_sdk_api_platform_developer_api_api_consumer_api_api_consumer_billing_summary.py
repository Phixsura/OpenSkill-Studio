"""API Consumer Billing Summary — comprehensive billing overview per consumer."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class BillingSummary:
    consumer_id: str
    period: str
    base_cost_cents: int = 0
    usage_cost_cents: int = 0
    overage_cost_cents: int = 0
    discount_cents: int = 0
    total_requests: int = 0
    tier: str = "free"

    @property
    def total_cents(self) -> int:
        return max(0, self.base_cost_cents + self.usage_cost_cents + self.overage_cost_cents - self.discount_cents)

    @property
    def total_dollars(self) -> str:
        return f"${self.total_cents / 100:.2f}"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerBillingSummary:
    def __init__(self) -> None:
        self._summaries: dict[tuple[str, str, str], BillingSummary] = {}

    def create_summary(self, installation_id: str, summary: BillingSummary) -> BillingSummary:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, summary.consumer_id, summary.period)
        self._summaries[key] = summary
        return summary

    def get_summary(self, installation_id: str, consumer_id: str, period: str) -> BillingSummary | None:
        return self._summaries.get((installation_id, consumer_id, period))

    def total_revenue(self, installation_id: str, period: str) -> int:
        return sum(s.total_cents for (inst, _, p), s in self._summaries.items() if inst == installation_id and p == period)

    def top_spenders(self, installation_id: str, period: str, limit: int = 5) -> list[BillingSummary]:
        summaries = [s for (inst, _, p), s in self._summaries.items() if inst == installation_id and p == period]
        return sorted(summaries, key=lambda s: -s.total_cents)[:limit]

    def list_summaries(self, installation_id: str, consumer_id: str | None = None) -> list[BillingSummary]:
        summaries = [s for (inst, _, _), s in self._summaries.items() if inst == installation_id]
        if consumer_id: summaries = [s for s in summaries if s.consumer_id == consumer_id]
        return summaries
