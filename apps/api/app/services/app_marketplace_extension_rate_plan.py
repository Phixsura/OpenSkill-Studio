"""Rate Plan — manage tiered API rate limits per pricing plan.

Associates rate limit configurations with pricing plans, enabling
different quotas for free, starter, pro, and enterprise tiers.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RatePlanConfig:
    plan_id: str
    plan_name: str
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    concurrent_connections: int
    bandwidth_mb_per_day: int


DEFAULT_PLANS: dict[str, RatePlanConfig] = {
    "free": RatePlanConfig("free", "Free", 60, 1000, 10000, 10, 5, 100),
    "starter": RatePlanConfig("starter", "Starter", 300, 10000, 100000, 30, 20, 1000),
    "pro": RatePlanConfig("pro", "Professional", 1000, 50000, 500000, 100, 50, 10000),
    "enterprise": RatePlanConfig("enterprise", "Enterprise", 5000, 200000, 2000000, 500, 200, 100000),
}


class RatePlanService:
    """Manages API rate limits per pricing plan."""

    def __init__(self):
        self._plans = dict(DEFAULT_PLANS)
        self._org_plans: dict[str, str] = {}  # org_id -> plan_id
        self._overrides: dict[str, dict] = {}  # org_id -> partial overrides

    def get_plan(self, plan_id: str) -> RatePlanConfig | None:
        return self._plans.get(plan_id)

    def assign_plan(self, org_id: str, plan_id: str) -> bool:
        if plan_id not in self._plans:
            return False
        self._org_plans[org_id] = plan_id
        return True

    def get_org_plan(self, org_id: str) -> RatePlanConfig:
        plan_id = self._org_plans.get(org_id, "free")
        return self._plans[plan_id]

    def set_override(self, org_id: str, overrides: dict) -> None:
        """Set custom rate limit overrides for an org."""
        self._overrides[org_id] = overrides

    def get_effective_limits(self, org_id: str) -> dict:
        """Get effective rate limits (plan + overrides)."""
        plan = self.get_org_plan(org_id)
        limits = {
            "requests_per_minute": plan.requests_per_minute,
            "requests_per_hour": plan.requests_per_hour,
            "requests_per_day": plan.requests_per_day,
            "burst_limit": plan.burst_limit,
            "concurrent_connections": plan.concurrent_connections,
            "bandwidth_mb_per_day": plan.bandwidth_mb_per_day,
        }
        overrides = self._overrides.get(org_id, {})
        limits.update(overrides)
        return {"org_id": org_id, "plan": plan.plan_name, "limits": limits, "has_overrides": bool(overrides)}

    def compare_plans(self, plan_a: str, plan_b: str) -> dict:
        a = self._plans.get(plan_a)
        b = self._plans.get(plan_b)
        if not a or not b:
            return {"error": "Plan not found"}
        return {
            "plan_a": plan_a, "plan_b": plan_b,
            "differences": {
                "requests_per_minute": {"a": a.requests_per_minute, "b": b.requests_per_minute},
                "requests_per_hour": {"a": a.requests_per_hour, "b": b.requests_per_hour},
                "requests_per_day": {"a": a.requests_per_day, "b": b.requests_per_day},
                "burst_limit": {"a": a.burst_limit, "b": b.burst_limit},
            },
        }

    def list_plans(self) -> list[dict]:
        return [{"id": p.plan_id, "name": p.plan_name, "rpm": p.requests_per_minute,
                 "rpd": p.requests_per_day} for p in self._plans.values()]
