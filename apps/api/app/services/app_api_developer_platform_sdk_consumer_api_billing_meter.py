"""Consumer Billing Meter — usage-based billing with tiered pricing."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class PricingTier:
    up_to: int | None  # None = unlimited
    unit_price_cents: int  # price per unit in cents


@dataclass
class BillingPlan:
    plan_id: str
    name: str
    base_price_cents: int = 0
    tiers: list[PricingTier] = field(default_factory=list)
    included_units: int = 0


@dataclass
class UsageRecord:
    consumer_id: str
    period: str
    units: int = 0


@dataclass
class BillingMeter:
    """Track usage and calculate bills with tiered pricing."""

    _plans: dict[str, BillingPlan] = field(default_factory=dict)
    _assignments: dict[str, str] = field(default_factory=dict)  # consumer -> plan_id
    _usage: dict[str, dict[str, int]] = field(default_factory=dict)  # consumer -> {period: units}

    def create_plan(self, plan: BillingPlan) -> dict:
        if plan.plan_id in self._plans:
            raise ValueError(f"Plan {plan.plan_id} already exists")
        self._plans[plan.plan_id] = plan
        logger.info("billing_plan_created", plan_id=plan.plan_id)
        return {"plan_id": plan.plan_id, "name": plan.name}

    def assign_plan(self, consumer_id: str, plan_id: str) -> dict:
        if plan_id not in self._plans:
            raise ValueError(f"Plan {plan_id} not found")
        self._assignments[consumer_id] = plan_id
        return {"consumer_id": consumer_id, "plan_id": plan_id}

    def record_usage(self, consumer_id: str, period: str, units: int) -> dict:
        if units < 0:
            raise ValueError("Units must be non-negative")
        usage = self._usage.setdefault(consumer_id, {})
        usage[period] = usage.get(period, 0) + units
        logger.info("usage_recorded", consumer_id=consumer_id, period=period, units=units)
        return {"consumer_id": consumer_id, "period": period, "total_units": usage[period]}

    def calculate_bill(self, consumer_id: str, period: str) -> dict:
        plan_id = self._assignments.get(consumer_id)
        if not plan_id:
            return {"error": "no_plan_assigned"}
        plan = self._plans.get(plan_id)
        if not plan:
            return {"error": "plan_not_found"}
        total_units = self._usage.get(consumer_id, {}).get(period, 0)
        billable_units = max(0, total_units - plan.included_units)
        # Calculate tiered cost
        tiered_cost = 0
        remaining = billable_units
        for tier in plan.tiers:
            if remaining <= 0:
                break
            if tier.up_to is None:
                tier_units = remaining
            else:
                tier_units = min(remaining, tier.up_to)
            tiered_cost += tier_units * tier.unit_price_cents
            remaining -= tier_units
        # If no tiers defined and there are remaining units, no extra charge
        total_cents = plan.base_price_cents + tiered_cost
        return {
            "consumer_id": consumer_id,
            "period": period,
            "plan_name": plan.name,
            "total_units": total_units,
            "included_units": plan.included_units,
            "billable_units": billable_units,
            "base_price_cents": plan.base_price_cents,
            "usage_price_cents": tiered_cost,
            "total_cents": total_cents,
            "total_dollars": round(total_cents / 100, 2),
        }

    def get_usage_summary(self, consumer_id: str) -> dict:
        usage = self._usage.get(consumer_id, {})
        periods = sorted(usage.keys())
        return {
            "consumer_id": consumer_id,
            "periods": len(periods),
            "total_units": sum(usage.values()),
            "by_period": {p: usage[p] for p in periods},
        }

    def list_plans(self) -> list[dict]:
        return [
            {"plan_id": p.plan_id, "name": p.name, "base_cents": p.base_price_cents,
             "included_units": p.included_units, "tier_count": len(p.tiers)}
            for p in self._plans.values()
        ]
