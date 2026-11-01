"""Extension API Rate Plan — tiered rate limiting plans."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RatePlan:
    plan_id: str
    name: str
    requests_per_minute: int
    requests_per_day: int
    burst_limit: int
    price_cents_monthly: int = 0


class ExtApiRatePlanService:
    def __init__(self):
        self._plans: dict[str, RatePlan] = {}
        self._assignments: dict[str, str] = {}  # ext_id -> plan_id
        self._seed()

    def _seed(self):
        plans = [
            RatePlan("free", "Free", 60, 10000, 10, 0),
            RatePlan("starter", "Starter", 300, 50000, 50, 999),
            RatePlan("pro", "Pro", 1000, 500000, 200, 4999),
            RatePlan("enterprise", "Enterprise", 5000, 5000000, 1000, 19999),
        ]
        for p in plans:
            self._plans[p.plan_id] = p

    def assign(self, extension_id: str, plan_id: str) -> bool:
        if plan_id not in self._plans: return False
        self._assignments[extension_id] = plan_id
        return True

    def get_limits(self, extension_id: str) -> RatePlan:
        plan_id = self._assignments.get(extension_id, "free")
        return self._plans[plan_id]

    def get_all_plans(self) -> list[RatePlan]:
        return sorted(self._plans.values(), key=lambda p: p.price_cents_monthly)

    def check_within_limit(self, extension_id: str, current_rpm: int) -> tuple[bool, int]:
        plan = self.get_limits(extension_id)
        return current_rpm < plan.requests_per_minute, plan.requests_per_minute - current_rpm
