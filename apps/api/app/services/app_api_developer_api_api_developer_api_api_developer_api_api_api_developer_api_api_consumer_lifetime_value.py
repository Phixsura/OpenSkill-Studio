"""App API Developer Consumer Lifetime Value — calculate consumer LTV."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerLTV:
    consumer_id: str
    total_spend_cents: int = 0
    months_active: int = 0
    current_mrr_cents: int = 0
    plan: str = "free"
    churn_risk: str = "low"  # "low", "medium", "high"

    @property
    def ltv_cents(self) -> int:
        if self.months_active == 0: return 0
        avg_monthly = self.total_spend_cents / self.months_active
        return int(avg_monthly * 24)  # 24-month projected LTV

    @property
    def arpu_cents(self) -> int:
        return int(self.total_spend_cents / self.months_active) if self.months_active > 0 else 0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValue:
    def __init__(self) -> None:
        self._consumers: dict[tuple[str, str], ConsumerLTV] = {}

    def update(self, installation_id: str, consumer_id: str, total_spend_cents: int, months_active: int, current_mrr_cents: int, plan: str, churn_risk: str = "low") -> ConsumerLTV:
        if not installation_id: raise ValueError("installation_id is required")
        if churn_risk not in ("low", "medium", "high"): raise ValueError("invalid churn_risk")
        key = (installation_id, consumer_id)
        c = ConsumerLTV(consumer_id=consumer_id, total_spend_cents=total_spend_cents, months_active=months_active, current_mrr_cents=current_mrr_cents, plan=plan, churn_risk=churn_risk)
        self._consumers[key] = c
        return c

    def top_ltv(self, installation_id: str, limit: int = 10) -> list[ConsumerLTV]:
        consumers = [c for (inst, _), c in self._consumers.items() if inst == installation_id]
        return sorted(consumers, key=lambda c: c.ltv_cents, reverse=True)[:limit]

    def at_risk(self, installation_id: str) -> list[ConsumerLTV]:
        return [c for (inst, _), c in self._consumers.items() if inst == installation_id and c.churn_risk == "high"]

    def total_mrr_cents(self, installation_id: str) -> int:
        return sum(c.current_mrr_cents for (inst, _), c in self._consumers.items() if inst == installation_id)
