"""Analysis runner (ADR-017 §10, §12): aggregates snapshot sufficient
statistics, drives the pure core in services/analysis.py, enforces the
sequential look budget, and stamps every run into the audit trail with a
canonical result hash (decisions must reference the hash — no
decide-before-analyze, exp06).

Randomized vs observational is surfaced on every response: observational
analyses NEVER claim causality (causal_claim: false + caveat)."""

import hashlib
import json
import math
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models import (
    Experiment,
    ExperimentEvent,
    ExperimentVersion,
    MetricDefinition,
    MetricSnapshot,
)
from app.experiments.schemas import ExperimentSpec
from app.experiments.services import analysis as stats
from app.models.user import User

_ANALYZABLE_STATUSES = frozenset({"running", "paused", "completed", "analyzed"})

_SUM_FIELDS = ("n", "numerator", "denominator", "sum_value", "sum_sq",
               "cov_sum", "cov_sum_sq", "cov_xy_sum")


def result_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _spec(self, exp: Experiment) -> ExperimentSpec:
        latest = (
            await self.db.execute(
                select(ExperimentVersion).where(
                    ExperimentVersion.experiment_id == exp.id,
                    ExperimentVersion.version == exp.current_version,
                )
            )
        ).scalar_one_or_none()
        if latest is None:
            raise AppError("EXPERIMENT_SPEC_INVALID", "Experiment has no spec version", 422)
        try:
            return ExperimentSpec.model_validate(latest.spec)
        except Exception as exc:  # noqa: BLE001 — typed 422 beats a raw 500
            raise AppError(
                "EXPERIMENT_SPEC_INVALID", "Stored spec failed to parse", 422
            ) from exc

    async def _aggregate_metric(
        self, experiment_id: str, metric_key: str
    ) -> tuple[dict[str, dict], bool]:
        """Sum sufficient stats across windows per variant, restricted to the
        HIGHEST query_version present; returns (per-variant stats, mixed?)."""
        rows = list(
            (
                await self.db.execute(
                    select(MetricSnapshot).where(
                        MetricSnapshot.experiment_id == experiment_id,
                        MetricSnapshot.metric_key == metric_key,
                    )
                )
            ).scalars()
        )
        if not rows:
            return {}, False
        versions = {int(r.provenance.get("query_version", 1)) for r in rows}
        use_version = max(versions)
        mixed = len(versions) > 1
        aggregated: dict[str, dict] = {}
        for row in rows:
            if int(row.provenance.get("query_version", 1)) != use_version:
                continue
            arm = aggregated.setdefault(row.variant_key, dict.fromkeys(_SUM_FIELDS))
            for field in _SUM_FIELDS:
                value = getattr(row, field)
                if value is None:
                    continue
                arm[field] = (arm[field] or 0) + float(value)
        return aggregated, mixed

    @staticmethod
    def _compare(
        kind: str, engine: str, control: dict, treatment: dict
    ) -> dict:
        if kind in ("binary", "time_to_event"):
            x1 = control.get("numerator") or 0.0
            n1 = control.get("denominator") or 0.0
            x2 = treatment.get("numerator") or 0.0
            n2 = treatment.get("denominator") or 0.0
            if engine == "bayesian":
                result = stats.bayes_binary(x1, n1, x2, n2)
            else:
                result = stats.analyze_binary(x1, n1, x2, n2)
            if kind == "time_to_event":
                result["caveat"] = "time_to_event analyzed as binary-at-horizon (full KM in exp10)"
            return result
        if kind == "rate":
            result = stats.analyze_rate(
                control.get("numerator") or 0.0, control.get("denominator") or 0.0,
                treatment.get("numerator") or 0.0, treatment.get("denominator") or 0.0,
            )
            if engine == "bayesian" and not result.get("insufficient_data"):
                # Normal-approximation posterior over the rate difference
                se, effect = result["se"], result["effect"]
                z0 = effect / se if se > 0 else 0.0
                result["p_beat_control"] = stats.norm_cdf(z0)
                result["expected_loss"] = max(
                    0.0,
                    se * math.exp(-z0 * z0 / 2.0) / math.sqrt(2 * math.pi)
                    - effect * stats.norm_sf(z0),
                ) if se > 0 else 0.0
                result["credible_interval"] = result["ci"]
            return result
        # continuous
        args = (
            control.get("n") or 0.0, control.get("sum_value") or 0.0,
            control.get("sum_sq") or 0.0,
            treatment.get("n") or 0.0, treatment.get("sum_value") or 0.0,
            treatment.get("sum_sq") or 0.0,
        )
        if engine == "bayesian":
            result = stats.bayes_continuous(*args)
        else:
            result = stats.welch_from_stats(*args)
        cuped = stats.cuped_adjusted_welch(
            {"n": control.get("n"), "sum": control.get("sum_value"),
             "sum_sq": control.get("sum_sq"), "cov_sum": control.get("cov_sum"),
             "cov_sum_sq": control.get("cov_sum_sq"), "cov_xy_sum": control.get("cov_xy_sum")},
            {"n": treatment.get("n"), "sum": treatment.get("sum_value"),
             "sum_sq": treatment.get("sum_sq"), "cov_sum": treatment.get("cov_sum"),
             "cov_sum_sq": treatment.get("cov_sum_sq"), "cov_xy_sum": treatment.get("cov_xy_sum")},
        )
        if cuped is not None:
            result["cuped"] = {
                "effect": cuped["effect"], "ci": cuped["ci"], "p": cuped["p"],
                "theta": cuped["theta"],
                "variance_reduction_pct": cuped["variance_reduction_pct"],
            }
        return result

    async def run(self, experiment_id: str, *, actor: User) -> dict:
        exp = await self.db.get(Experiment, experiment_id)
        if not exp:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        if exp.status not in _ANALYZABLE_STATUSES:
            raise AppError(
                "VALIDATION_ERROR",
                f"Analysis requires status in {sorted(_ANALYZABLE_STATUSES)} (got {exp.status})",
                422,
            )
        spec = await self._spec(exp)

        # Sequential look budget (O'Brien-Fleming only; mSPRT peeks freely)
        look_number = None
        boundary_z = None
        if spec.sequential == "obrien_fleming":
            used = (
                await self.db.execute(
                    select(func.count()).where(
                        ExperimentEvent.experiment_id == experiment_id,
                        ExperimentEvent.event_type == "analysis_look",
                    )
                )
            ).scalar_one()
            if used >= spec.stop_policy.max_looks:
                raise AppError(
                    "EXPERIMENT_LOOKS_EXHAUSTED",
                    f"All {spec.stop_policy.max_looks} O'Brien-Fleming looks used",
                    422,
                )
            look_number = used + 1
            boundary_z = stats.obrien_fleming_boundary(
                look_number, spec.stop_policy.max_looks
            )

        control_key = next(v.key for v in spec.variants if v.is_control)
        definitions = {
            d.key: d
            for d in (
                await self.db.execute(
                    select(MetricDefinition).where(
                        MetricDefinition.key.in_(
                            [*spec.metrics.primary, *spec.metrics.secondary]
                        )
                    )
                )
            ).scalars()
        }

        warnings: list[str] = []
        if spec.design in ("cluster", "switchback"):
            warnings.append("CLUSTERED_DESIGN_NAIVE_SE")
        # Honesty warnings: spec knobs accepted but not (yet) applied must be
        # surfaced, never silently ignored
        if spec.trigger.analysis_population == "exposed":
            warnings.append("TRIGGERED_ANALYSIS_UNAPPLIED")

        metrics_out: dict[str, dict] = {}
        secondary_ps: dict[str, float] = {}
        for role, keys in (("primary", spec.metrics.primary), ("secondary", spec.metrics.secondary)):
            for key in keys:
                definition = definitions.get(key)
                aggregated, mixed = await self._aggregate_metric(experiment_id, key)
                if mixed and "SNAPSHOT_VERSION_MIXED" not in warnings:
                    warnings.append("SNAPSHOT_VERSION_MIXED")
                entry: dict = {"role": role}
                if not aggregated or control_key not in aggregated:
                    entry["insufficient_data"] = True
                    metrics_out[key] = entry
                    continue
                kind = definition.kind if definition else (
                    "binary" if aggregated[control_key].get("denominator") else "continuous"
                )
                entry["kind"] = kind
                if definition:
                    entry["direction"] = definition.direction
                comparisons = {}
                for variant_key, arm in aggregated.items():
                    if variant_key == control_key:
                        continue
                    comparison = self._compare(
                        kind, spec.stats_engine, aggregated[control_key], arm
                    )
                    # Sequential adjustment on the standardized statistic.
                    # NOT `get("z") or get("t")` — a legitimate z of exactly
                    # 0.0 is falsy and would silently drop the sequential
                    # fields (falsy-zero class).
                    z = comparison.get("z")
                    if z is None:
                        z = comparison.get("t")
                    if z is not None and spec.sequential == "msprt":
                        comparison["always_valid_p"] = stats.msprt_always_valid_p(z)
                    if z is not None and boundary_z is not None:
                        comparison["boundary_z"] = boundary_z
                        comparison["significant_at_boundary"] = abs(z) > boundary_z
                    comparisons[variant_key] = comparison
                    if role == "secondary" and comparison.get("p") is not None:
                        secondary_ps[f"{key}:{variant_key}"] = comparison["p"]
                entry["comparisons"] = comparisons
                metrics_out[key] = entry

        if spec.variance_reduction is not None:
            any_cuped = any(
                "cuped" in comparison
                for metric in metrics_out.values()
                for comparison in (metric.get("comparisons") or {}).values()
            )
            if not any_cuped:
                # Configured but no source computed covariate aggregates yet
                warnings.append("CUPED_COVARIATES_UNAVAILABLE")

        if secondary_ps:
            fdr = stats.benjamini_hochberg(secondary_ps)
            for combo, passes in fdr.items():
                key, variant_key = combo.split(":", 1)
                metrics_out[key]["comparisons"][variant_key]["passes_fdr"] = passes

        causal = spec.analysis_type == "randomized"
        payload: dict = {
            "experiment_id": experiment_id,
            "experiment_key": exp.key,
            "engine": spec.stats_engine,
            "sequential": spec.sequential,
            "analysis_type": spec.analysis_type,
            "causal_claim": causal,
            "control": control_key,
            "metrics": metrics_out,
            "warnings": warnings,
        }
        if not causal:
            payload["caveat"] = (
                "Observational analysis — associations only; no causal claim "
                "and no promotion eligibility (ADR-017 §10)."
            )
        if look_number is not None:
            payload["looks"] = {"used": look_number, "max": spec.stop_policy.max_looks}
        payload["result_hash"] = result_hash(
            {k: payload[k] for k in ("metrics", "engine", "analysis_type", "control")}
        )

        # Audit: every analysis run lands a look event (budget enforced above
        # for OF; mSPRT records for traceability only)
        self.db.add(
            ExperimentEvent(
                experiment_id=experiment_id,
                actor_user_id=actor.id,
                event_type="analysis_look",
                payload={
                    "sequential": spec.sequential,
                    "look": look_number,
                    "result_hash": payload["result_hash"],
                    "at": datetime.now(UTC).isoformat(),
                },
            )
        )
        await self.db.flush()
        return payload
