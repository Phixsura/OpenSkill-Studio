"""App Plan Manager — manage subscription plans and features for installed apps.

Manages subscription plan definitions:
- Define plans with feature sets
- Check feature access by plan
- Plan comparison
- Per-installation plan assignment
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Plan:
    """A subscription plan."""

    plan_id: str
    name: str
    features: set[str] = field(default_factory=set)
    price_cents: int = 0
    tier: int = 0  # ordering (0 = lowest)


class AppPlanManager:
    """Manage subscription plans and feature access."""

    def __init__(self) -> None:
        self._plans: dict[str, Plan] = {}
        # installation_id → plan_id
        self._assignments: dict[str, str] = {}

    def define_plan(
        self,
        plan_id: str,
        name: str,
        features: list[str],
        price_cents: int = 0,
        tier: int = 0,
    ) -> Plan:
        """Define a subscription plan."""
        if not plan_id:
            raise ValueError("plan_id is required")
        if not name:
            raise ValueError("name is required")

        plan = Plan(
            plan_id=plan_id, name=name,
            features=set(features), price_cents=price_cents, tier=tier,
        )
        self._plans[plan_id] = plan
        return plan

    def assign_plan(self, installation_id: str, plan_id: str) -> None:
        """Assign a plan to an installation."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if plan_id not in self._plans:
            raise KeyError(f"Plan {plan_id} not found")
        self._assignments[installation_id] = plan_id

    def get_plan(self, installation_id: str) -> Plan | None:
        """Get the assigned plan for an installation."""
        plan_id = self._assignments.get(installation_id)
        if plan_id is None:
            return None
        return self._plans.get(plan_id)

    def has_feature(self, installation_id: str, feature: str) -> bool:
        """Check if an installation's plan includes a feature."""
        plan = self.get_plan(installation_id)
        if plan is None:
            return False
        return feature in plan.features

    def compare_plans(self, plan_a_id: str, plan_b_id: str) -> dict:
        """Compare features between two plans."""
        a = self._plans.get(plan_a_id)
        b = self._plans.get(plan_b_id)
        if a is None or b is None:
            raise KeyError("One or both plans not found")

        return {
            "only_in_a": sorted(a.features - b.features),
            "only_in_b": sorted(b.features - a.features),
            "shared": sorted(a.features & b.features),
        }

    def list_plans(self) -> list[Plan]:
        """List all plans sorted by tier."""
        return sorted(self._plans.values(), key=lambda p: p.tier)

    def get_upgrade_options(self, installation_id: str) -> list[Plan]:
        """Get plans higher than current."""
        current = self.get_plan(installation_id)
        if current is None:
            return self.list_plans()
        return [p for p in self.list_plans() if p.tier > current.tier]
