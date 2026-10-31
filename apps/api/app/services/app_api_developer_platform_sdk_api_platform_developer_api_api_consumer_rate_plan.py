"""API Consumer Rate Plan — assign and manage rate plans per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class RatePlan:
    plan_id: str
    name: str
    requests_per_minute: int
    requests_per_day: int
    burst_size: int = 20
    priority: int = 0  # higher = more priority

@dataclass
class ConsumerPlan:
    consumer_id: str
    plan_id: str
    minute_count: int = 0
    day_count: int = 0
    overages: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerRatePlan:
    def __init__(self) -> None:
        self._plans: dict[tuple[str, str], RatePlan] = {}
        self._assignments: dict[tuple[str, str], ConsumerPlan] = {}

    def create_plan(self, installation_id: str, plan: RatePlan) -> RatePlan:
        if not installation_id: raise ValueError("installation_id is required")
        if plan.requests_per_minute < 1: raise ValueError("requests_per_minute must be >= 1")
        if plan.requests_per_day < plan.requests_per_minute: raise ValueError("daily limit must be >= per-minute limit")
        key = (installation_id, plan.plan_id)
        if key in self._plans: raise ValueError(f"Plan {plan.plan_id} exists")
        self._plans[key] = plan
        return plan

    def assign(self, installation_id: str, consumer_id: str, plan_id: str) -> ConsumerPlan:
        if (installation_id, plan_id) not in self._plans: raise KeyError(f"Plan {plan_id} not found")
        key = (installation_id, consumer_id)
        existing = self._assignments.get(key)
        if existing: existing.plan_id = plan_id; return existing
        cp = ConsumerPlan(consumer_id=consumer_id, plan_id=plan_id)
        self._assignments[key] = cp
        return cp

    def check_limit(self, installation_id: str, consumer_id: str) -> dict[str, object]:
        cp = self._assignments.get((installation_id, consumer_id))
        if cp is None: return {"allowed": True, "reason": "no_plan"}
        plan = self._plans.get((installation_id, cp.plan_id))
        if plan is None: return {"allowed": True, "reason": "plan_missing"}
        if cp.minute_count >= plan.requests_per_minute:
            return {"allowed": False, "reason": "minute_limit", "limit": plan.requests_per_minute}
        if cp.day_count >= plan.requests_per_day:
            return {"allowed": False, "reason": "day_limit", "limit": plan.requests_per_day}
        return {"allowed": True, "remaining_minute": plan.requests_per_minute - cp.minute_count, "remaining_day": plan.requests_per_day - cp.day_count}

    def record_request(self, installation_id: str, consumer_id: str) -> ConsumerPlan:
        cp = self._assignments.get((installation_id, consumer_id))
        if cp is None: raise KeyError(f"No plan for {consumer_id}")
        cp.minute_count += 1
        cp.day_count += 1
        return cp

    def list_plans(self, installation_id: str) -> list[RatePlan]:
        return [p for (inst, _), p in self._plans.items() if inst == installation_id]
