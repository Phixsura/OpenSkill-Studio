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

    @staticmethod
    def _validate_guardrails(guardrails: dict | None) -> dict:
        """§11.4 shape check: {"min_samples": int>=0, "thresholds": {dim: float>=0}}."""
        if not guardrails:
            return {"min_samples": 0, "thresholds": {}}
        if not isinstance(guardrails, dict):
            raise AppError("VALIDATION_ERROR", "guardrails must be an object", 422)
        min_samples = guardrails.get("min_samples", 0)
        if not isinstance(min_samples, int) or min_samples < 0 or min_samples > 100_000:
            raise AppError("VALIDATION_ERROR", "guardrails.min_samples must be int >= 0", 422)
        thresholds = guardrails.get("thresholds", {})
        if not isinstance(thresholds, dict):
            raise AppError("VALIDATION_ERROR", "guardrails.thresholds must be an object", 422)
        clean: dict[str, float] = {}
        for dim, value in thresholds.items():
            if dim not in _COMPARE_DIMENSIONS:
                raise AppError(
                    "VALIDATION_ERROR",
                    f"Unknown guarded dimension: {dim} (allowed: {sorted(_COMPARE_DIMENSIONS)})",
                    422,
                )
            try:
                numeric = float(value)
            except (TypeError, ValueError) as exc:
                raise AppError("VALIDATION_ERROR", f"Threshold {dim} not numeric", 422) from exc
            if numeric != numeric or numeric < 0:
                raise AppError("VALIDATION_ERROR", f"Threshold {dim} must be >= 0", 422)
            clean[str(dim)] = numeric
        return {"min_samples": min_samples, "thresholds": clean}

    async def create(
        self,
        *,
        replacement_candidate_id: str,
        scope_type: str,
        scope_ref: str | None = None,
        guardrails: dict | None = None,
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
            guardrails=self._validate_guardrails(guardrails),
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
        """Collect candidate metrics; compute per-dimension deltas, sample size
        and guardrail regressions (§11.4)."""
        from sqlalchemy import select

        from app.ecosystem.models.benchmark import BenchmarkResult
        from app.ecosystem.services.benchmark import latest_completed_run
        from app.ecosystem.services.stats import two_proportion_z_test, welch_t_test

        plan = await self.get(plan_id)
        self._check_transition(plan, "evaluating")
        candidate = await self.db.get(ReplacementCandidate, plan.replacement_candidate_id)
        candidate_run = await latest_completed_run(
            self.db, candidate.candidate_kind, candidate.candidate_id
        )
        # Baseline per-result samples for significance testing (LaunchDarkly
        # lesson taken further: raw deltas never call a regression alone —
        # a guarded regression must also be statistically significant when
        # per-sample data exists on both sides)
        baseline_run = await latest_completed_run(
            self.db, candidate.deprecated_kind, candidate.deprecated_id
        )

        async def _samples(run) -> dict:
            if run is None:
                return {"latency": [], "cost": [], "successes": 0, "n": 0}
            rows = list(
                await self.db.scalars(
                    select(BenchmarkResult).where(BenchmarkResult.run_id == run.id)
                )
            )
            return {
                "latency": [float(r.latency_ms) for r in rows if r.latency_ms is not None],
                "cost": [float(r.cost_usd or 0) for r in rows],
                "successes": sum(1 for r in rows if not r.failed),
                "n": len(rows),
            }

        cand_samples = await _samples(candidate_run)
        base_samples = await _samples(baseline_run)
        candidate_metrics = dict(candidate_run.dimension_scores or {}) if candidate_run else {}
        sample_size = cand_samples["n"]

        # Per-dimension significance tests where raw samples exist
        tests: dict[str, dict] = {}
        if cand_samples["latency"] and base_samples["latency"]:
            tests["speed_p50_ms"] = welch_t_test(cand_samples["latency"], base_samples["latency"])
        if cand_samples["cost"] and base_samples["cost"]:
            tests["cost_per_case_usd"] = welch_t_test(cand_samples["cost"], base_samples["cost"])
        if cand_samples["n"] and base_samples["n"]:
            tests["reliability"] = two_proportion_z_test(
                cand_samples["successes"], cand_samples["n"],
                base_samples["successes"], base_samples["n"],
            )

        guardrails = plan.guardrails or {}
        thresholds: dict = guardrails.get("thresholds", {}) or {}
        comparison: dict = {"sample_size": sample_size, "baseline_sample_size": base_samples["n"]}
        regressions: list[str] = []
        for dim, higher_is_better in _COMPARE_DIMENSIONS.items():
            base = (plan.baseline or {}).get(dim)
            cand = candidate_metrics.get(dim)
            if base is None or cand is None:
                continue
            delta = float(cand) - float(base)
            entry = {
                "baseline": float(base),
                "candidate": float(cand),
                "delta": round(delta, 6),
                "improved": (delta > 0) if higher_is_better else (delta < 0),
            }
            test = tests.get(dim)
            if test is not None:
                entry["p_value"] = test["p_value"]
                entry["significant"] = test["p_value"] < 0.05
            # Guarded dimension: regression = worsens beyond its threshold AND,
            # when a significance test exists, the difference is significant —
            # noise never blocks a promote, real regressions always do
            if dim in thresholds:
                threshold = float(thresholds[dim])
                beyond = delta < -threshold if higher_is_better else delta > threshold
                regressed = beyond and (test is None or test["p_value"] < 0.05)
                entry["threshold"] = threshold
                entry["regression"] = regressed
                if regressed:
                    regressions.append(dim)
            comparison[dim] = entry
        comparison["regressions"] = regressions
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
        # Row lock: concurrent decisions serialize — the loser re-reads a
        # terminal status and is refused, so the promotion side effect
        # (recommended_replacement edge) is recorded exactly once.
        await self.db.refresh(plan, with_for_update=True)
        if decision == "promote":
            if plan.status in ("draft", "running"):
                raise AppError(
                    "ECO_ROLLOUT_NOT_EVALUATED",
                    "Run evaluation before promoting",
                    409,
                )
            self._check_transition(plan, "promoted")
            # §11.4 guardrails — promote refused, never silently overridden.
            # Revising thresholds is an explicit human act on the plan.
            guardrails = plan.guardrails or {}
            comparison = plan.comparison or {}
            min_samples = int(guardrails.get("min_samples", 0) or 0)
            if int(comparison.get("sample_size", 0) or 0) < min_samples:
                raise AppError(
                    "ECO_ROLLOUT_INSUFFICIENT_SAMPLES",
                    f"Candidate has {comparison.get('sample_size', 0)} benchmark "
                    f"samples; guardrail requires >= {min_samples}",
                    409,
                )
            regressions = comparison.get("regressions") or []
            if regressions:
                raise AppError(
                    "ECO_ROLLOUT_REGRESSION",
                    f"Guarded dimensions regressed beyond threshold: {regressions}",
                    409,
                )
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
