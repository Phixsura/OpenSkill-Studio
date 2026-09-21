"""Controlled rollout / canary validation (ADR-016 Part M).

Old-vs-candidate comparison within an explicit scope. Promote/reject are
explicit human decisions; promotion records a replacement edge + lifecycle
recommendation and NEVER rewrites existing production bindings.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.replacement import (
    ROLLOUT_SCOPES,
    ReplacementCandidate,
    RolloutPlan,
)
from app.ecosystem.services.benchmark import latest_dimension_scores
from app.exceptions import AppError

_STATUS_FLOW = {
    "draft": {"running", "aborted"},
    "running": {"evaluating", "aborted"},
    "evaluating": {"promoted", "rejected", "aborted"},
    "promoted": set(),
    "rejected": set(),
    "aborted": set(),
}

# Dimensions compared during evaluation (higher_is_better flag)
_COMPARE_DIMENSIONS = {
    "quality": True,
    "reliability": True,
    "commercial_readiness": True,
    "cost_per_case_usd": False,
    "speed_p50_ms": False,
}


class RolloutService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        replacement_candidate_id: str,
        scope_type: str,
        scope_ref: str | None = None,
    ) -> RolloutPlan:
        if scope_type not in ROLLOUT_SCOPES:
            raise AppError("VALIDATION_ERROR", f"Unknown scope type: {scope_type}", 422)
        if scope_type != "benchmark_only" and not scope_ref:
            raise AppError("VALIDATION_ERROR", f"scope_ref required for {scope_type}", 422)
        candidate = await self.db.get(ReplacementCandidate, replacement_candidate_id)
        if not candidate:
            raise AppError("NOT_FOUND", "Replacement candidate not found", 404)
        if not candidate.hard_compatible:
            raise AppError(
                "ECO_HARD_INCOMPATIBLE",
                "Cannot roll out a hard-incompatible candidate",
                409,
            )
        baseline = await latest_dimension_scores(
            self.db, candidate.deprecated_kind, candidate.deprecated_id
        )
        plan = RolloutPlan(
            replacement_candidate_id=replacement_candidate_id,
            scope_type=scope_type,
            scope_ref=scope_ref,
            baseline=baseline,
        )
        self.db.add(plan)
        await self.db.flush()
        return plan

    async def get(self, plan_id: str) -> RolloutPlan:
        plan = await self.db.get(RolloutPlan, plan_id)
        if not plan:
            raise AppError("NOT_FOUND", "Rollout plan not found", 404)
        return plan

    async def list(self, *, status: str | None = None, limit: int = 50) -> list[RolloutPlan]:
        query = select(RolloutPlan)
        if status:
            query = query.where(RolloutPlan.status == status)
        rows = await self.db.scalars(query.order_by(RolloutPlan.created_at.desc()).limit(limit))
        return list(rows)

    def _check_transition(self, plan: RolloutPlan, to_status: str) -> None:
        if to_status not in _STATUS_FLOW.get(plan.status, set()):
            raise AppError(
                "ECO_INVALID_TRANSITION",
                f"Cannot move rollout {plan.status} -> {to_status}",
                409,
            )

    async def start(self, plan_id: str) -> RolloutPlan:
        plan = await self.get(plan_id)
        self._check_transition(plan, "running")
        plan.status = "running"
        await self.db.flush()
        return plan

    async def evaluate(self, plan_id: str) -> RolloutPlan:
        """Collect candidate metrics and compute per-dimension deltas."""
        plan = await self.get(plan_id)
        self._check_transition(plan, "evaluating")
        candidate = await self.db.get(ReplacementCandidate, plan.replacement_candidate_id)
        candidate_metrics = await latest_dimension_scores(
            self.db, candidate.candidate_kind, candidate.candidate_id
        )
        comparison: dict = {}
        for dim, higher_is_better in _COMPARE_DIMENSIONS.items():
            base = (plan.baseline or {}).get(dim)
            cand = candidate_metrics.get(dim)
            if base is None or cand is None:
                continue
            delta = float(cand) - float(base)
            comparison[dim] = {
                "baseline": float(base),
                "candidate": float(cand),
                "delta": round(delta, 6),
                "improved": (delta > 0) if higher_is_better else (delta < 0),
            }
        plan.candidate_metrics = candidate_metrics
        plan.comparison = comparison
        plan.status = "evaluating"
        await self.db.flush()
        return plan

    async def decide(
        self, plan_id: str, *, decision: str, actor_id: str, note: str | None = None
    ) -> RolloutPlan:
        """Explicit human promote/reject/abort."""
        plan = await self.get(plan_id)
        if decision == "promote":
            if plan.status in ("draft", "running"):
                raise AppError(
                    "ECO_ROLLOUT_NOT_EVALUATED",
                    "Run evaluation before promoting",
                    409,
                )
            self._check_transition(plan, "promoted")
            candidate = await self.db.get(
                ReplacementCandidate, plan.replacement_candidate_id
            )
            # Promotion records the recommendation — never rewrites bindings
            from app.ecosystem.services.replacement import ReplacementService

            await ReplacementService(self.db).add_edge(
                from_kind=candidate.deprecated_kind,
                from_id=candidate.deprecated_id,
                to_kind=candidate.candidate_kind,
                to_id=candidate.candidate_id,
                edge_type="recommended_replacement",
                rationale=f"Rollout {plan.id} promoted",
                created_by=actor_id,
            )
            plan.status = "promoted"
        elif decision == "reject":
            self._check_transition(plan, "rejected")
            plan.status = "rejected"
        elif decision == "abort":
            self._check_transition(plan, "aborted")
            plan.status = "aborted"
        else:
            raise AppError("VALIDATION_ERROR", f"Unknown decision: {decision}", 422)
        plan.decided_by = actor_id
        plan.decided_at = datetime.now(UTC)
        plan.note = note
        await self.db.flush()
        return plan
