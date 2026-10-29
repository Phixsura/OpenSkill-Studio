"""App API Developer Consumer Billing Profile — per-consumer billing and plan management."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class BillingProfile:
    consumer_id: str
    plan: str  # "free", "starter", "pro", "enterprise"
    billing_email: str
    monthly_budget_cents: int = 0
    current_spend_cents: int = 0
    auto_upgrade: bool = False
    created_at: float = field(default_factory=time.time)

    @property
    def budget_usage_pct(self) -> float:
        return round(self.current_spend_cents / self.monthly_budget_cents * 100, 1) if self.monthly_budget_cents > 0 else 0.0

    @property
    def over_budget(self) -> bool:
        return self.monthly_budget_cents > 0 and self.current_spend_cents > self.monthly_budget_cents

class AppAPIDeveloperAPIApiDeveloperApiApiConsumerBillingProfile:
    def __init__(self) -> None:
        self._profiles: dict[tuple[str, str], BillingProfile] = {}

    def create(self, installation_id: str, consumer_id: str, plan: str, billing_email: str, monthly_budget_cents: int = 0) -> BillingProfile:
        if not installation_id: raise ValueError("installation_id is required")
        if plan not in ("free", "starter", "pro", "enterprise"): raise ValueError("invalid plan")
        if "@" not in billing_email: raise ValueError("invalid email")
        key = (installation_id, consumer_id)
        p = BillingProfile(consumer_id=consumer_id, plan=plan, billing_email=billing_email, monthly_budget_cents=monthly_budget_cents)
        self._profiles[key] = p
        return p

    def add_charge(self, installation_id: str, consumer_id: str, amount_cents: int) -> BillingProfile:
        if amount_cents < 0: raise ValueError("amount must be non-negative")
        p = self._get(installation_id, consumer_id)
        p.current_spend_cents += amount_cents
        return p

    def upgrade_plan(self, installation_id: str, consumer_id: str, new_plan: str) -> BillingProfile:
        plans = ["free", "starter", "pro", "enterprise"]
        p = self._get(installation_id, consumer_id)
        if plans.index(new_plan) <= plans.index(p.plan): raise ValueError("Can only upgrade to a higher plan")
        p.plan = new_plan
        return p

    def over_budget_consumers(self, installation_id: str) -> list[BillingProfile]:
        return [p for (inst, _), p in self._profiles.items() if inst == installation_id and p.over_budget]

    def by_plan(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), p in self._profiles.items():
            if inst == installation_id: counts[p.plan] = counts.get(p.plan, 0) + 1
        return counts

    def _get(self, installation_id: str, consumer_id: str) -> BillingProfile:
        key = (installation_id, consumer_id)
        p = self._profiles.get(key)
        if p is None: raise KeyError(f"Profile {consumer_id} not found")
        return p
