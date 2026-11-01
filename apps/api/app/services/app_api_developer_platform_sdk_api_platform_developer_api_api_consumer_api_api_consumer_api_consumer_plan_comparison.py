"""API Consumer Plan Comparison — compare pricing plans side by side."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PlanDetails:
    plan_id: str
    name: str
    monthly_price_cents: int
    requests_per_month: int
    rate_limit_rps: int
    features: list[str] = field(default_factory=list)
    support_level: str = "community"  # "community", "email", "priority", "dedicated"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerPlanComparison:
    def __init__(self) -> None:
        self._plans: dict[tuple[str, str], PlanDetails] = {}

    def add_plan(self, installation_id: str, plan: PlanDetails) -> PlanDetails:
        if not installation_id: raise ValueError("installation_id is required")
        if plan.monthly_price_cents < 0: raise ValueError("Price must be non-negative")
        key = (installation_id, plan.plan_id)
        if key in self._plans: raise ValueError(f"Plan {plan.plan_id} already exists")
        self._plans[key] = plan
        return plan

    def compare(self, installation_id: str, plan_ids: list[str]) -> list[PlanDetails]:
        return [self._plans[(installation_id, pid)] for pid in plan_ids if (installation_id, pid) in self._plans]

    def recommend(self, installation_id: str, monthly_requests: int) -> PlanDetails | None:
        plans = [p for (inst, _), p in self._plans.items() if inst == installation_id and p.requests_per_month >= monthly_requests]
        if not plans: return None
        return min(plans, key=lambda p: p.monthly_price_cents)

    def list_plans(self, installation_id: str) -> list[PlanDetails]:
        return sorted([p for (inst, _), p in self._plans.items() if inst == installation_id], key=lambda p: p.monthly_price_cents)
