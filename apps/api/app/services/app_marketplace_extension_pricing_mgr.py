"""Extension Pricing Manager — manage pricing plans for extensions."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PricingPlan:
    plan_id: str
    name: str
    price_cents: int  # 0 = free
    interval: str = "monthly"  # monthly, yearly, one_time
    features: list[str] = field(default_factory=list)
    trial_days: int = 0
    active: bool = True


class ExtPricingMgrService:
    def __init__(self):
        self._plans: dict[str, dict[str, PricingPlan]] = {}  # ext_id -> {plan_id -> plan}

    def create_plan(self, extension_id: str, plan_id: str, name: str,
                    price_cents: int, interval: str = "monthly",
                    features: list[str] | None = None, trial_days: int = 0) -> PricingPlan:
        if price_cents < 0:
            raise ValueError("Price cannot be negative")
        plan = PricingPlan(plan_id=plan_id, name=name, price_cents=price_cents,
                           interval=interval, features=features or [], trial_days=trial_days)
        if extension_id not in self._plans:
            self._plans[extension_id] = {}
        self._plans[extension_id][plan_id] = plan
        return plan

    def get_plans(self, extension_id: str) -> list[PricingPlan]:
        return [p for p in self._plans.get(extension_id, {}).values() if p.active]

    def deactivate(self, extension_id: str, plan_id: str) -> bool:
        plan = self._plans.get(extension_id, {}).get(plan_id)
        if plan:
            plan.active = False
            return True
        return False

    def get_cheapest(self, extension_id: str) -> PricingPlan | None:
        plans = self.get_plans(extension_id)
        paid = [p for p in plans if p.price_cents > 0]
        return min(paid, key=lambda p: p.price_cents) if paid else None

    def has_free_tier(self, extension_id: str) -> bool:
        return any(p.price_cents == 0 for p in self.get_plans(extension_id))

    def format_price(self, price_cents: int) -> str:
        if price_cents == 0:
            return "Free"
        return f"${price_cents / 100:.2f}"
