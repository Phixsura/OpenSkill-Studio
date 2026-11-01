"""App API Rate Plan — manage tiered rate limiting plans.

Manages rate limit plans:
- Define plans with request limits per time window
- Assign plans to tenants/tokens
- Check rate limit status
- Per-installation scoped plans
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class RatePlan:
    """A rate limiting plan."""

    plan_id: str
    name: str
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int = 0  # 0 = no burst


@dataclass
class RateWindow:
    """Rate tracking for a window."""

    count: int = 0
    window_start: float = field(default_factory=time.time)


class AppAPIRatePlan:
    """Manage tiered rate limiting plans."""

    def __init__(self) -> None:
        self._plans: dict[tuple[str, str], RatePlan] = {}
        self._assignments: dict[tuple[str, str], str] = {}  # (inst, tenant) → plan_id
        self._counters: dict[tuple[str, str, str], RateWindow] = {}  # (inst, tenant, window_type)

    def create_plan(
        self, installation_id: str, plan_id: str, name: str,
        rpm: int, rph: int, rpd: int, burst: int = 0,
    ) -> RatePlan:
        if not installation_id:
            raise ValueError("installation_id is required")
        if rpm < 0 or rph < 0 or rpd < 0:
            raise ValueError("limits must be non-negative")

        plan = RatePlan(
            plan_id=plan_id, name=name,
            requests_per_minute=rpm, requests_per_hour=rph,
            requests_per_day=rpd, burst_limit=burst,
        )
        self._plans[(installation_id, plan_id)] = plan
        return plan

    def assign_plan(self, installation_id: str, tenant_id: str, plan_id: str) -> None:
        if (installation_id, plan_id) not in self._plans:
            raise KeyError(f"Plan {plan_id} not found")
        self._assignments[(installation_id, tenant_id)] = plan_id

    def check_limit(self, installation_id: str, tenant_id: str) -> dict:
        """Check current rate limit status."""
        plan_id = self._assignments.get((installation_id, tenant_id))
        if plan_id is None:
            return {"allowed": True, "plan": None}

        plan = self._plans.get((installation_id, plan_id))
        if plan is None:
            return {"allowed": True, "plan": None}

        now = time.time()
        minute_key = (installation_id, tenant_id, "minute")
        hour_key = (installation_id, tenant_id, "hour")

        # Check minute window
        mw = self._counters.get(minute_key)
        if mw and (now - mw.window_start) < 60:
            if mw.count >= plan.requests_per_minute:
                return {"allowed": False, "reason": "rpm_exceeded", "plan": plan.name}
        elif mw:
            mw.count = 0
            mw.window_start = now

        return {"allowed": True, "plan": plan.name}

    def record_request(self, installation_id: str, tenant_id: str) -> None:
        now = time.time()
        minute_key = (installation_id, tenant_id, "minute")
        mw = self._counters.get(minute_key)
        if mw is None or (now - mw.window_start) >= 60:
            self._counters[minute_key] = RateWindow(count=1, window_start=now)
        else:
            mw.count += 1

    def list_plans(self, installation_id: str) -> list[RatePlan]:
        return [p for (inst, _), p in self._plans.items() if inst == installation_id]

    def tenant_plan(self, installation_id: str, tenant_id: str) -> RatePlan | None:
        plan_id = self._assignments.get((installation_id, tenant_id))
        if plan_id is None:
            return None
        return self._plans.get((installation_id, plan_id))
