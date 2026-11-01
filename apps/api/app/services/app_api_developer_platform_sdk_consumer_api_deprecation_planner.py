"""Endpoint Deprecation Planner — deprecation timeline with migration tracking."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

PHASES = ("announced", "warning", "migration", "sunset", "removed")


@dataclass
class DeprecationPlan:
    plan_id: str
    old_endpoint: str
    new_endpoint: str
    phase: str = "announced"
    announce_date: str = ""
    sunset_date: str = ""
    migration_guide_url: str = ""
    consumers_migrated: set[str] = field(default_factory=set)
    consumers_remaining: set[str] = field(default_factory=set)


@dataclass
class DeprecationPlanner:
    """Plan and track endpoint deprecation with consumer migration."""

    _plans: dict[str, DeprecationPlan] = field(default_factory=dict)

    def create_plan(self, plan_id: str, old_endpoint: str, new_endpoint: str,
                    announce_date: str, sunset_date: str,
                    affected_consumers: list[str] | None = None) -> dict:
        if plan_id in self._plans:
            raise ValueError(f"Plan {plan_id} already exists")
        plan = DeprecationPlan(
            plan_id=plan_id, old_endpoint=old_endpoint,
            new_endpoint=new_endpoint, announce_date=announce_date,
            sunset_date=sunset_date,
            consumers_remaining=set(affected_consumers or []),
        )
        self._plans[plan_id] = plan
        logger.info("deprecation_planned", plan_id=plan_id, old=old_endpoint)
        return {"plan_id": plan_id, "affected_consumers": len(plan.consumers_remaining)}

    def advance_phase(self, plan_id: str) -> dict:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        idx = PHASES.index(plan.phase)
        if idx >= len(PHASES) - 1:
            raise ValueError("Already at final phase")
        plan.phase = PHASES[idx + 1]
        logger.info("phase_advanced", plan_id=plan_id, phase=plan.phase)
        return {"plan_id": plan_id, "phase": plan.phase}

    def mark_migrated(self, plan_id: str, consumer_id: str) -> dict:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        plan.consumers_remaining.discard(consumer_id)
        plan.consumers_migrated.add(consumer_id)
        total = len(plan.consumers_migrated) + len(plan.consumers_remaining)
        pct = round(len(plan.consumers_migrated) / total * 100, 1) if total > 0 else 100
        return {"consumer_id": consumer_id, "migrated": True,
                "migration_pct": pct, "remaining": len(plan.consumers_remaining)}

    def get_plan(self, plan_id: str) -> dict | None:
        plan = self._plans.get(plan_id)
        if not plan:
            return None
        total = len(plan.consumers_migrated) + len(plan.consumers_remaining)
        pct = round(len(plan.consumers_migrated) / total * 100, 1) if total > 0 else 100
        return {
            "plan_id": plan.plan_id,
            "old_endpoint": plan.old_endpoint,
            "new_endpoint": plan.new_endpoint,
            "phase": plan.phase,
            "announce_date": plan.announce_date,
            "sunset_date": plan.sunset_date,
            "migrated": len(plan.consumers_migrated),
            "remaining": len(plan.consumers_remaining),
            "migration_pct": pct,
            "ready_to_sunset": len(plan.consumers_remaining) == 0,
        }

    def list_plans(self, phase: str | None = None) -> list[dict]:
        plans = list(self._plans.values())
        if phase:
            plans = [p for p in plans if p.phase == phase]
        return [self.get_plan(p.plan_id) for p in plans]

    def get_consumer_migrations(self, consumer_id: str) -> list[dict]:
        results = []
        for plan in self._plans.values():
            if consumer_id in plan.consumers_remaining:
                results.append({"plan_id": plan.plan_id, "old": plan.old_endpoint,
                                "new": plan.new_endpoint, "status": "pending",
                                "sunset_date": plan.sunset_date})
            elif consumer_id in plan.consumers_migrated:
                results.append({"plan_id": plan.plan_id, "old": plan.old_endpoint,
                                "new": plan.new_endpoint, "status": "migrated"})
        return results

    def get_stats(self) -> dict:
        plans = list(self._plans.values())
        by_phase = {p: sum(1 for pl in plans if pl.phase == p) for p in PHASES}
        total_remaining = sum(len(p.consumers_remaining) for p in plans)
        return {
            "total_plans": len(plans),
            "by_phase": by_phase,
            "consumers_pending_migration": total_remaining,
        }
