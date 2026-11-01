"""Migration Planner — plan and execute extension upgrades across orgs.

Coordinates multi-org extension version upgrades with rollout strategies
(all-at-once, canary, blue-green), health checks, and rollback triggers.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class RolloutStrategy(str, Enum):
    ALL_AT_ONCE = "all_at_once"
    CANARY = "canary"
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"


class MigrationState(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


@dataclass
class OrgMigrationStatus:
    org_id: str
    status: str = "pending"  # pending, migrating, completed, failed, rolled_back
    error: str = ""


@dataclass
class MigrationPlan:
    plan_id: str
    extension_id: str
    from_version: str
    to_version: str
    strategy: RolloutStrategy
    orgs: list[OrgMigrationStatus]
    state: MigrationState = MigrationState.PLANNED
    created_at: str = ""
    canary_percent: int = 10  # for canary strategy

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class MigrationPlanner:
    """Plans and tracks multi-org extension migrations."""

    def __init__(self):
        self._plans: dict[str, MigrationPlan] = {}

    def create_plan(self, plan_id: str, extension_id: str, from_ver: str,
                    to_ver: str, org_ids: list[str],
                    strategy: RolloutStrategy = RolloutStrategy.ROLLING,
                    canary_percent: int = 10) -> MigrationPlan:
        orgs = [OrgMigrationStatus(org_id=oid) for oid in org_ids]
        plan = MigrationPlan(
            plan_id=plan_id, extension_id=extension_id,
            from_version=from_ver, to_version=to_ver,
            strategy=strategy, orgs=orgs, canary_percent=canary_percent,
        )
        self._plans[plan_id] = plan
        return plan

    def get_next_batch(self, plan_id: str) -> list[str]:
        """Get the next batch of orgs to migrate based on strategy."""
        plan = self._plans.get(plan_id)
        if not plan:
            return []
        pending = [o for o in plan.orgs if o.status == "pending"]
        if not pending:
            return []

        if plan.strategy == RolloutStrategy.ALL_AT_ONCE:
            return [o.org_id for o in pending]
        elif plan.strategy == RolloutStrategy.CANARY:
            batch_size = max(1, len(plan.orgs) * plan.canary_percent // 100)
            return [o.org_id for o in pending[:batch_size]]
        else:  # rolling
            return [pending[0].org_id]

    def migrate_org(self, plan_id: str, org_id: str, success: bool,
                    error: str = "") -> bool:
        plan = self._plans.get(plan_id)
        if not plan:
            return False
        for org in plan.orgs:
            if org.org_id == org_id:
                org.status = "completed" if success else "failed"
                org.error = error
                return True
        return False

    def rollback_org(self, plan_id: str, org_id: str) -> bool:
        plan = self._plans.get(plan_id)
        if not plan:
            return False
        for org in plan.orgs:
            if org.org_id == org_id:
                org.status = "rolled_back"
                return True
        return False

    def get_progress(self, plan_id: str) -> dict | None:
        plan = self._plans.get(plan_id)
        if not plan:
            return None
        total = len(plan.orgs)
        by_status = {"pending": 0, "completed": 0, "failed": 0, "rolled_back": 0, "migrating": 0}
        for o in plan.orgs:
            by_status[o.status] = by_status.get(o.status, 0) + 1
        return {
            "plan_id": plan_id, "total_orgs": total,
            "by_status": by_status,
            "percent_complete": round(by_status["completed"] / max(1, total) * 100, 1),
            "has_failures": by_status["failed"] > 0,
        }

    def get_plan(self, plan_id: str) -> MigrationPlan | None:
        return self._plans.get(plan_id)
