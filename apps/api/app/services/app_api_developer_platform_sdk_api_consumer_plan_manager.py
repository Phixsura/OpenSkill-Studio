"""App API Developer Consumer Plan Manager — manage consumer subscription plans."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

PLANS = {
    "free": {"api_calls": 10000, "webhooks": 1000, "rate_limit": 10},
    "starter": {"api_calls": 100000, "webhooks": 10000, "rate_limit": 100},
    "pro": {"api_calls": 1000000, "webhooks": 100000, "rate_limit": 1000},
    "enterprise": {"api_calls": -1, "webhooks": -1, "rate_limit": 10000},  # -1 = unlimited
}

@dataclass
class ConsumerPlan:
    consumer_id: str
    plan: str
    limits: dict[str, int] = field(default_factory=dict)
    upgraded_at: float = field(default_factory=time.time)
    previous_plan: str = ""

class AppAPIDeveloperPlatformSDKApiConsumerPlanManager:
    def __init__(self) -> None:
        self._plans: dict[tuple[str, str], ConsumerPlan] = {}

    def assign(self, installation_id: str, consumer_id: str, plan: str) -> ConsumerPlan:
        if not installation_id: raise ValueError("installation_id is required")
        if plan not in PLANS: raise ValueError(f"Unknown plan: {plan}")
        key = (installation_id, consumer_id)
        existing = self._plans.get(key)
        previous = existing.plan if existing else ""
        c = ConsumerPlan(consumer_id=consumer_id, plan=plan, limits=dict(PLANS[plan]), previous_plan=previous)
        self._plans[key] = c
        return c

    def get(self, installation_id: str, consumer_id: str) -> ConsumerPlan | None:
        return self._plans.get((installation_id, consumer_id))

    def by_plan(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), c in self._plans.items():
            if inst == installation_id: counts[c.plan] = counts.get(c.plan, 0) + 1
        return counts

    def check_limit(self, installation_id: str, consumer_id: str, resource: str) -> int:
        c = self._plans.get((installation_id, consumer_id))
        if c is None: return PLANS["free"].get(resource, 0)
        return c.limits.get(resource, 0)

    def all_consumers(self, installation_id: str) -> list[ConsumerPlan]:
        return [c for (inst, _), c in self._plans.items() if inst == installation_id]
