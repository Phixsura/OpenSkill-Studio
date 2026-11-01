"""Rate Plan Manager — manage tiered API rate plans with burst allowance."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class RatePlan:
    plan_id: str
    name: str
    requests_per_minute: int
    requests_per_day: int
    burst_size: int = 0
    price_cents: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class PlanAssignment:
    consumer_id: str
    plan_id: str
    assigned_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    current_minute_count: int = 0
    current_day_count: int = 0
    burst_remaining: int = 0


@dataclass
class RatePlanManager:
    """Manage tiered rate plans and check consumer limits."""

    _plans: dict[str, RatePlan] = field(default_factory=dict)
    _assignments: dict[str, PlanAssignment] = field(default_factory=dict)

    def create_plan(self, plan: RatePlan) -> dict:
        if plan.plan_id in self._plans:
            raise ValueError(f"Plan {plan.plan_id} already exists")
        if plan.requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        if plan.requests_per_day <= 0:
            raise ValueError("requests_per_day must be positive")
        self._plans[plan.plan_id] = plan
        logger.info("rate_plan_created", plan_id=plan.plan_id, name=plan.name)
        return {"plan_id": plan.plan_id, "name": plan.name}

    def assign_plan(self, consumer_id: str, plan_id: str) -> dict:
        if plan_id not in self._plans:
            raise ValueError(f"Plan {plan_id} not found")
        plan = self._plans[plan_id]
        self._assignments[consumer_id] = PlanAssignment(
            consumer_id=consumer_id,
            plan_id=plan_id,
            burst_remaining=plan.burst_size,
        )
        logger.info("plan_assigned", consumer_id=consumer_id, plan_id=plan_id)
        return {"consumer_id": consumer_id, "plan_id": plan_id}

    def check_limit(self, consumer_id: str) -> dict:
        assignment = self._assignments.get(consumer_id)
        if not assignment:
            return {"consumer_id": consumer_id, "allowed": False, "reason": "no_plan"}
        plan = self._plans.get(assignment.plan_id)
        if not plan:
            return {"consumer_id": consumer_id, "allowed": False, "reason": "plan_deleted"}
        if assignment.current_day_count >= plan.requests_per_day:
            return {"consumer_id": consumer_id, "allowed": False, "reason": "daily_limit"}
        if assignment.current_minute_count >= plan.requests_per_minute:
            if assignment.burst_remaining > 0:
                assignment.burst_remaining -= 1
                assignment.current_minute_count += 1
                assignment.current_day_count += 1
                return {"consumer_id": consumer_id, "allowed": True, "used_burst": True,
                        "burst_remaining": assignment.burst_remaining}
            return {"consumer_id": consumer_id, "allowed": False, "reason": "minute_limit"}
        assignment.current_minute_count += 1
        assignment.current_day_count += 1
        return {"consumer_id": consumer_id, "allowed": True, "used_burst": False}

    def get_usage(self, consumer_id: str) -> dict:
        assignment = self._assignments.get(consumer_id)
        if not assignment:
            return {"consumer_id": consumer_id, "status": "unassigned"}
        plan = self._plans.get(assignment.plan_id)
        if not plan:
            return {"consumer_id": consumer_id, "status": "plan_missing"}
        return {
            "consumer_id": consumer_id,
            "plan_id": assignment.plan_id,
            "plan_name": plan.name,
            "minute_usage": f"{assignment.current_minute_count}/{plan.requests_per_minute}",
            "day_usage": f"{assignment.current_day_count}/{plan.requests_per_day}",
            "burst_remaining": assignment.burst_remaining,
            "minute_pct": round(assignment.current_minute_count / plan.requests_per_minute * 100, 1),
            "day_pct": round(assignment.current_day_count / plan.requests_per_day * 100, 1),
        }

    def list_plans(self) -> list[dict]:
        return [
            {"plan_id": p.plan_id, "name": p.name, "rpm": p.requests_per_minute,
             "rpd": p.requests_per_day, "burst": p.burst_size, "price_cents": p.price_cents}
            for p in sorted(self._plans.values(), key=lambda x: x.price_cents)
        ]

    def reset_minute(self, consumer_id: str) -> dict:
        assignment = self._assignments.get(consumer_id)
        if not assignment:
            return {"status": "not_found"}
        assignment.current_minute_count = 0
        plan = self._plans.get(assignment.plan_id)
        if plan:
            assignment.burst_remaining = plan.burst_size
        return {"consumer_id": consumer_id, "minute_reset": True}
