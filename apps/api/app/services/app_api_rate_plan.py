"""App API Rate Plan — tiered rate plan assignment and enforcement for developer apps.

Maps apps to rate limit tiers based on their marketplace plan:
- Plan tiers with per-endpoint rate limits
- Burst allowance configuration
- Plan upgrade/downgrade with instant enforcement
- Usage-to-plan ratio reporting
- Overage tracking for billing
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class PlanTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


@dataclass(frozen=True)
class RatePlanLimits:
    """Rate limits for a plan tier."""

    requests_per_second: int
    requests_per_minute: int
    requests_per_hour: int
    burst_size: int              # max concurrent burst
    daily_quota: int
    webhook_deliveries_per_hour: int
    sandbox_executions_per_hour: int


PLAN_LIMITS: dict[PlanTier, RatePlanLimits] = {
    PlanTier.FREE: RatePlanLimits(
        requests_per_second=2, requests_per_minute=60, requests_per_hour=1_000,
        burst_size=5, daily_quota=5_000,
        webhook_deliveries_per_hour=50, sandbox_executions_per_hour=20,
    ),
    PlanTier.STARTER: RatePlanLimits(
        requests_per_second=10, requests_per_minute=300, requests_per_hour=10_000,
        burst_size=20, daily_quota=50_000,
        webhook_deliveries_per_hour=500, sandbox_executions_per_hour=200,
    ),
    PlanTier.GROWTH: RatePlanLimits(
        requests_per_second=50, requests_per_minute=1_500, requests_per_hour=50_000,
        burst_size=100, daily_quota=500_000,
        webhook_deliveries_per_hour=5_000, sandbox_executions_per_hour=2_000,
    ),
    PlanTier.ENTERPRISE: RatePlanLimits(
        requests_per_second=200, requests_per_minute=6_000, requests_per_hour=200_000,
        burst_size=500, daily_quota=2_000_000,
        webhook_deliveries_per_hour=50_000, sandbox_executions_per_hour=20_000,
    ),
}


@dataclass
class AppPlanAssignment:
    """An app's assigned rate plan."""

    app_id: str
    tier: PlanTier
    assigned_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    overages: int = 0           # count of quota exceeded events


@dataclass
class PlanCheckResult:
    """Result of checking an app's plan limits."""

    allowed: bool
    tier: PlanTier
    limit_name: str
    limit_value: int
    current_usage: int
    remaining: int


class AppApiRatePlan:
    """Manage rate plan assignments and enforcement."""

    def __init__(self):
        self._assignments: dict[str, AppPlanAssignment] = {}
        # (app_id, day_key) → daily request count
        self._daily_usage: dict[tuple[str, str], int] = {}

    def assign(self, app_id: str, tier: PlanTier) -> AppPlanAssignment:
        assignment = AppPlanAssignment(app_id=app_id, tier=tier)
        self._assignments[app_id] = assignment
        log.info("rate_plan.assigned", app_id=app_id, tier=tier.value)
        return assignment

    def get_assignment(self, app_id: str) -> AppPlanAssignment | None:
        return self._assignments.get(app_id)

    def get_limits(self, app_id: str) -> RatePlanLimits:
        assignment = self._assignments.get(app_id)
        tier = assignment.tier if assignment else PlanTier.FREE
        return PLAN_LIMITS[tier]

    def upgrade(self, app_id: str, new_tier: PlanTier) -> AppPlanAssignment:
        current = self._assignments.get(app_id)
        if current and _tier_rank(new_tier) <= _tier_rank(current.tier):
            raise ValueError(f"Cannot upgrade from {current.tier.value} to {new_tier.value}")
        return self.assign(app_id, new_tier)

    def downgrade(self, app_id: str, new_tier: PlanTier) -> AppPlanAssignment:
        current = self._assignments.get(app_id)
        if current and _tier_rank(new_tier) >= _tier_rank(current.tier):
            raise ValueError(f"Cannot downgrade from {current.tier.value} to {new_tier.value}")
        return self.assign(app_id, new_tier)

    def record_usage(self, app_id: str, count: int = 1) -> PlanCheckResult:
        """Record API usage and check daily quota."""
        limits = self.get_limits(app_id)
        day_key = datetime.now(UTC).strftime("%Y-%m-%d")
        usage_key = (app_id, day_key)
        current = self._daily_usage.get(usage_key, 0)
        new_total = current + count
        self._daily_usage[usage_key] = new_total

        assignment = self._assignments.get(app_id)
        tier = assignment.tier if assignment else PlanTier.FREE

        if new_total > limits.daily_quota:
            if assignment:
                assignment.overages += 1
            return PlanCheckResult(
                allowed=False, tier=tier, limit_name="daily_quota",
                limit_value=limits.daily_quota, current_usage=new_total,
                remaining=0,
            )

        return PlanCheckResult(
            allowed=True, tier=tier, limit_name="daily_quota",
            limit_value=limits.daily_quota, current_usage=new_total,
            remaining=limits.daily_quota - new_total,
        )

    def get_daily_usage(self, app_id: str) -> int:
        day_key = datetime.now(UTC).strftime("%Y-%m-%d")
        return self._daily_usage.get((app_id, day_key), 0)

    def get_usage_ratio(self, app_id: str) -> float:
        """Usage as percentage of daily quota."""
        limits = self.get_limits(app_id)
        usage = self.get_daily_usage(app_id)
        return (usage / limits.daily_quota * 100) if limits.daily_quota > 0 else 0.0

    def list_assignments(self, tier: PlanTier | None = None) -> list[AppPlanAssignment]:
        assignments = list(self._assignments.values())
        if tier:
            assignments = [a for a in assignments if a.tier == tier]
        return sorted(assignments, key=lambda a: a.app_id)


def _tier_rank(tier: PlanTier) -> int:
    return {PlanTier.FREE: 0, PlanTier.STARTER: 1, PlanTier.GROWTH: 2, PlanTier.ENTERPRISE: 3}[tier]
