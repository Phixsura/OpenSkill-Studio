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
    def _latest_version_rows(rows: list) -> list:
        """Restrict window rows to the HIGHEST query_version present — the
        same rule _aggregate_metric applies, so per-window passes (novelty,
        time-stratified) never mix metric definitions."""
        if not rows:
            return rows
        use = max(int(r.provenance.get("query_version", 1)) for r in rows)
        return [r for r in rows if int(r.provenance.get("query_version", 1)) == use]

    async def _time_strata(
        self, experiment_id: str, metric_key: str, control_key: str
    ) -> dict[str, list[tuple[float, float]]]:
        """Per-window (effect, se) strata per treatment variant, using the
        same engine the pooled comparison uses for the metric's shape."""
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
        by_window: dict = {}
        for row in self._latest_version_rows(rows):
            by_window.setdefault(row.window_start, {})[row.variant_key] = row
        strata: dict[str, list[tuple[float, float]]] = {}
        for _ws, variants in sorted(by_window.items()):
            control = variants.get(control_key)
            if control is None:
                continue
            for variant_key, row in variants.items():
                if variant_key == control_key:
                    continue
                if control.denominator and row.denominator:
                    result = stats.analyze_binary(
                        float(control.numerator or 0), float(control.denominator),
                        float(row.numerator or 0), float(row.denominator),
                    )
                elif (control.n or 0) >= 2 and (row.n or 0) >= 2:
                    result = stats.welch_from_stats(
                        float(control.n), float(control.sum_value or 0),
                        float(control.sum_sq or 0),
                        float(row.n), float(row.sum_value or 0),
                        float(row.sum_sq or 0),
                    )
                else:
                    continue
                if result.get("insufficient_data"):
                    continue
                effect, se = result.get("effect"), result.get("se")
                if effect is None or se is None:
                    continue
                strata.setdefault(variant_key, []).append((effect, se))
        return strata

    async def _corpus_prior(
        self, exp, metric_key: str, exclude_experiment_id: str
    ) -> dict | None:
        """Empirical prior over a metric's effect within a domain: the latest
        analysis_look effect of every OTHER experiment in the domain that
        reached a terminal decision (decided = the analysis was trusted
        enough to act on). Needs >= 3 historical effects; returns
        {n_experiments, mean, sd}."""
        from app.experiments.models import TERMINAL_DECISIONS, DecisionRecord

        decided = (
            await self.db.execute(
                select(DecisionRecord.experiment_id)
                .where(
                    DecisionRecord.domain == exp.domain,
                    DecisionRecord.decision.in_(TERMINAL_DECISIONS),
                    DecisionRecord.experiment_id != exclude_experiment_id,
                )
                .distinct()
            )
        ).scalars()
        decided_ids = list(decided)
        if len(decided_ids) < 3:
            return None
        effects: list[float] = []
        for experiment_id in decided_ids:
            event = (
                await self.db.execute(
                    select(ExperimentEvent)
                    .where(
                        ExperimentEvent.experiment_id == experiment_id,
                        ExperimentEvent.event_type == "analysis_look",
                    )
                    .order_by(ExperimentEvent.created_at.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()
            if event is None:
                continue
            per_metric = (event.payload or {}).get("primary_effects", {}).get(metric_key)
            if not per_metric:
                continue
            arm_effects = [
                v["effect"] for v in per_metric.values() if v.get("effect") is not None
            ]
            if arm_effects:
                effects.append(sum(arm_effects) / len(arm_effects))
        if len(effects) < 3:
            return None
        mean = sum(effects) / len(effects)
        var = sum((e - mean) ** 2 for e in effects) / (len(effects) - 1)
        return {
            "n_experiments": len(effects),
            "mean": mean,
            "sd": math.sqrt(var),
        }

    async def _novelty_suspect(
        self, experiment_id: str, metric_key: str, control_key: str
    ) -> bool:
        """Novelty / effect-decay health check (§4.6 v2): split the metric's
        snapshot windows at their midpoint and compare the pooled effect of
        the early half against the late half. A strong early effect
        (|z| > 3) that flips sign or shrinks to under a third late is the
        classic novelty signature — flagged, never auto-acted on."""
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
        rows = self._latest_version_rows(rows)
        starts = sorted({r.window_start for r in rows})
        if len(starts) < 4:  # need real windows on both sides of the split
            return False
        midpoint = starts[len(starts) // 2]

        def _pool(half_rows: list) -> dict[str, dict]:
            pooled: dict[str, dict] = {}
            for row in half_rows:
                arm = pooled.setdefault(row.variant_key, dict.fromkeys(_SUM_FIELDS))
                for field in _SUM_FIELDS:
                    value = getattr(row, field)
                    if value is None:
                        continue
                    arm[field] = (arm[field] or 0) + float(value)
            return pooled

        def _effect_z(pooled: dict[str, dict]) -> tuple[float, float] | None:
            control = pooled.get(control_key)
            treatments = [a for k, a in pooled.items() if k != control_key]
            if control is None or not treatments:
                return None
            arm = treatments[0]
            if control.get("denominator") and arm.get("denominator"):
                if control["denominator"] < 30 or arm["denominator"] < 30:
                    return None
                result = stats.analyze_binary(
                    control.get("numerator") or 0.0, control["denominator"],
                    arm.get("numerator") or 0.0, arm["denominator"],
                )
            elif (control.get("n") or 0) >= 30 and (arm.get("n") or 0) >= 30:
                result = stats.welch_from_stats(
                    control["n"], control.get("sum_value") or 0.0,
                    control.get("sum_sq") or 0.0,
                    arm["n"], arm.get("sum_value") or 0.0,
                    arm.get("sum_sq") or 0.0,
                )
            else:
                return None
            if result.get("insufficient_data"):
                return None
            z = result.get("z")
            if z is None:
                z = result.get("t")
            effect = result.get("effect")
            if z is None or effect is None:
                return None
            return effect, z

        early = _effect_z(_pool([r for r in rows if r.window_start < midpoint]))
        late = _effect_z(_pool([r for r in rows if r.window_start >= midpoint]))
        if early is None or late is None:
            return False
        early_effect, early_z = early
        late_effect, _late_z = late
        if abs(early_z) <= 3.0:
            return False
        if early_effect == 0.0:
            return False
        return (
            early_effect * late_effect < 0
            or abs(late_effect) < abs(early_effect) / 3.0
        )

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
            # Triggered analysis is applied at snapshot time (§4.7) — warn
            # only when stored snapshots predate the exposed-population
            # computation (their provenance lacks the marker)
            legacy = (
                await self.db.execute(
                    select(func.count()).where(
                        MetricSnapshot.experiment_id == experiment_id,
                        ~MetricSnapshot.provenance.has_key("analysis_population"),
                    )
                )
            ).scalar_one()
            if legacy:
                warnings.append("TRIGGERED_SNAPSHOTS_MIXED_POPULATION")
            warnings.append("TRIGGERED_DILUTION_UNCORRECTED")


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
                    # Pre-balance health check (§4.13): the covariate is
                    # PRE-experiment by construction, so its means must not
                    # differ across arms — a significant difference means the
                    # randomization (or the data feed) is broken, and every
                    # downstream effect estimate is suspect.
                    control_arm = aggregated[control_key]
                    if (
                        "PRE_BALANCE_SUSPECT" not in warnings
                        and all(
                            a.get("cov_sum") is not None
                            and a.get("cov_sum_sq") is not None
                            and (a.get("n") or 0) >= 2
                            for a in (control_arm, arm)
                        )
                    ):
                        balance = stats.welch_from_stats(
                            control_arm["n"], control_arm["cov_sum"],
                            control_arm["cov_sum_sq"],
                            arm["n"], arm["cov_sum"], arm["cov_sum_sq"],
                        )
                        p_balance = balance.get("p")
                        if p_balance is not None and p_balance < 0.001:
                            warnings.append("PRE_BALANCE_SUSPECT")
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

        # Post-stratification by time (§4.6 v2): per-window effects pooled
        # by inverse variance — robust to enrollment drift and time trends
        # that bias the naive pooled estimate. Informational alongside the
        # primary estimate.
        for key in spec.metrics.primary:
            entry = metrics_out.get(key)
            if not entry or not entry.get("comparisons"):
                continue
            strata_map = await self._time_strata(experiment_id, key, control_key)
            for variant_key, comparison in entry["comparisons"].items():
                pooled = stats.pool_stratified(strata_map.get(variant_key, []))
                if pooled is not None:
                    comparison["time_stratified"] = pooled

        # Meta-analysis corpus prior (§11 v2): effects this DOMAIN has
        # historically seen on the SAME primary metric, from decided
        # experiments — normal-normal shrinkage tempers day-one overreaction
        # to noisy effects. Informational: the unshrunk estimate stays the
        # decision basis; shrinkage is decision-support context.
        for key in spec.metrics.primary:
            prior = await self._corpus_prior(exp, key, experiment_id)
            if prior is None:
                continue
            entry = metrics_out.get(key)
            if not entry or not entry.get("comparisons"):
                continue
            for comparison in entry["comparisons"].values():
                effect, se = comparison.get("effect"), comparison.get("se")
                if effect is None or se is None or se <= 0 or prior["sd"] <= 0:
                    continue
                precision = 1.0 / (se * se) + 1.0 / (prior["sd"] * prior["sd"])
                shrunk = (
                    effect / (se * se) + prior["mean"] / (prior["sd"] * prior["sd"])
                ) / precision
                comparison["corpus_prior"] = prior
                comparison["shrunk_effect"] = shrunk

        for key in spec.metrics.primary:
            if await self._novelty_suspect(experiment_id, key, control_key):
                warnings.append("NOVELTY_EFFECT_DECAY_SUSPECT")
                break

        if spec.analysis_type == "observational":
            # Quasi-experiment support (§10 v2): where per-unit pre-period
            # covariates exist, attach a DiD change-score estimate. Still an
            # association — parallel trends is an assumption, not a test.
            for key in spec.metrics.primary:
                entry = metrics_out.get(key)
                if not entry or not entry.get("comparisons"):
                    continue
                aggregated, _mixed = await self._aggregate_metric(experiment_id, key)
                control_arm = aggregated.get(control_key)
                if not control_arm:
                    continue
                for variant_key, comparison in entry["comparisons"].items():
                    arm = aggregated.get(variant_key)
                    if not arm:
                        continue
                    did = stats.did_estimate(
                        {"n": control_arm.get("n"), "sum": control_arm.get("sum_value"),
                         "sum_sq": control_arm.get("sum_sq"),
                         "cov_sum": control_arm.get("cov_sum"),
                         "cov_sum_sq": control_arm.get("cov_sum_sq"),
                         "cov_xy_sum": control_arm.get("cov_xy_sum")},
                        {"n": arm.get("n"), "sum": arm.get("sum_value"),
                         "sum_sq": arm.get("sum_sq"), "cov_sum": arm.get("cov_sum"),
                         "cov_sum_sq": arm.get("cov_sum_sq"),
                         "cov_xy_sum": arm.get("cov_xy_sum")},
                    )
                    if did is not None:
                        comparison["did"] = {
                            **did,
                            "caveat": "parallel-trends assumed; association only",
                        }

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

        # Bandit allocation suggestion (§4.4 v2): Thompson weights over the
        # FIRST primary binary/rate metric. Advisory — shipping new weights
        # stays an operator decision (no auto-apply, ADR-017 §3 posture).
        if spec.allocation_mode == "bandit":
            for key in spec.metrics.primary:
                aggregated, _mixed = await self._aggregate_metric(experiment_id, key)
                arms = {
                    variant: (arm.get("numerator") or 0.0, arm.get("denominator") or 0.0)
                    for variant, arm in aggregated.items()
                    if arm.get("denominator")
                }
                suggestion = stats.thompson_weights(arms)
                if suggestion is not None:
                    payload_bandit = {"metric": key, **suggestion}
                    break
            else:
                payload_bandit = None
        else:
            payload_bandit = None

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
        if payload_bandit is not None:
            payload["bandit"] = payload_bandit
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
                    # Corpus raw material (§11 meta-analysis): the primary
                    # effects this look observed, se included
                    "primary_effects": {
                        key: {
                            variant: {
                                "effect": comparison.get("effect"),
                                "se": comparison.get("se"),
                            }
                            for variant, comparison in (
                                metrics_out[key].get("comparisons") or {}
                            ).items()
                            if comparison.get("effect") is not None
                        }
                        for key in spec.metrics.primary
                        if key in metrics_out
                    },
                },
            )
        )
        await self.db.flush()
        return payload
