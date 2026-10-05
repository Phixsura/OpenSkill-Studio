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
from datetime import UTC, datetime, timedelta

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
from app.models.user import User, UserRole

_ANALYZABLE_STATUSES = frozenset({"running", "paused", "completed", "analyzed"})

_SUM_FIELDS = ("n", "numerator", "denominator", "sum_value", "sum_sq",
               "cov_sum", "cov_sum_sq", "cov_xy_sum")


def result_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


ITS_DAYS = 14  # §10 v3: daily points per side for the interrupted series
SC_MAX_DONORS = 20  # §4.16: synthetic-control donor pool cap


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
        self, experiment_id: str, metric_key: str, segment: str = ""
    ) -> tuple[dict[str, dict], bool]:
        """Sum sufficient stats across windows per variant, restricted to the
        HIGHEST query_version present; returns (per-variant stats, mixed?).
        segment '' is the whole population — segment rows are a DISJOINT
        breakdown and must never mix into the top-level aggregate."""
        rows = list(
            (
                await self.db.execute(
                    select(MetricSnapshot).where(
                        MetricSnapshot.experiment_id == experiment_id,
                        MetricSnapshot.metric_key == metric_key,
                        MetricSnapshot.segment == segment,
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
            # §4.14 (round 124): histogram counts add across windows
            if getattr(row, "value_histogram", None):
                hacc = arm.setdefault("value_histogram", {})
                for bucket, count in row.value_histogram.items():
                    hacc[bucket] = hacc.get(bucket, 0) + int(count)
            # §4.6 v3 (round 115): fold the per-window covariates map —
            # sums, squares, xy and the xx cross terms all add across windows
            if row.covariates:
                acc = arm.setdefault("covariates", {})
                for cov_key, entry in row.covariates.items():
                    slot = acc.setdefault(
                        cov_key, {"sum": 0.0, "sum_sq": 0.0, "xy_sum": 0.0}
                    )
                    for f in ("sum", "sum_sq", "xy_sum"):
                        slot[f] += float(entry.get(f) or 0.0)
                    for other, xx in (entry.get("xx") or {}).items():
                        slot.setdefault("xx", {})
                        slot["xx"][other] = slot["xx"].get(other, 0.0) + float(xx)
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
                        MetricSnapshot.segment == "",
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
                        MetricSnapshot.segment == "",
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
        kind: str, engine: str, control: dict, treatment: dict,
        covariate_keys: list[str] | None = None, auto: bool = False,
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
                result["caveat"] = "time_to_event analyzed as binary-at-horizon (full KM deferred, ADR-017 §16)"
            # Round 142: regression adjustment on proportions — a 0/1 y has
            # sum == sum_sq == numerator, so the Welch CUPED cores apply
            # verbatim (Deng et al.'s linear adjustment; caveat attached)
            if covariate_keys and kind == "binary":
                y_control = {"n": n1, "sum": x1, "sum_sq": x1,
                             "covariates": control.get("covariates"),
                             "cov_sum": control.get("cov_sum"),
                             "cov_sum_sq": control.get("cov_sum_sq"),
                             "cov_xy_sum": control.get("cov_xy_sum")}
                y_treatment = {"n": n2, "sum": x2, "sum_sq": x2,
                               "covariates": treatment.get("covariates"),
                               "cov_sum": treatment.get("cov_sum"),
                               "cov_sum_sq": treatment.get("cov_sum_sq"),
                               "cov_xy_sum": treatment.get("cov_xy_sum")}
                adjusted = None
                if len(covariate_keys) > 1 or auto:
                    multi = stats.multi_cuped_adjusted_welch(
                        y_control, y_treatment, covariate_keys
                    )
                    if multi is not None:
                        adjusted = {
                            "effect": multi["effect"], "ci": multi["ci"],
                            "p": multi["p"], "theta": multi["theta"],
                            "variance_reduction_pct": multi["variance_reduction_pct"],
                            "covariates": covariate_keys,
                            "mode": "multi",
                        }
                if adjusted is None:
                    single = stats.cuped_adjusted_welch(y_control, y_treatment)
                    if single is not None:
                        adjusted = {
                            "effect": single["effect"], "ci": single["ci"],
                            "p": single["p"], "theta": single["theta"],
                            "variance_reduction_pct": single["variance_reduction_pct"],
                        }
                if adjusted is not None:
                    adjusted["caveat"] = (
                        "linear adjustment on a per-unit 0/1 outcome"
                    )
                    result["cuped"] = adjusted
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
        if covariate_keys and (len(covariate_keys) > 1 or auto):
            multi = stats.multi_cuped_adjusted_welch(
                {"n": control.get("n"), "sum": control.get("sum_value"),
                 "sum_sq": control.get("sum_sq"),
                 "covariates": control.get("covariates")},
                {"n": treatment.get("n"), "sum": treatment.get("sum_value"),
                 "sum_sq": treatment.get("sum_sq"),
                 "covariates": treatment.get("covariates")},
                covariate_keys,
            )
            if multi is not None:
                result["cuped"] = {
                    "effect": multi["effect"], "ci": multi["ci"],
                    "p": multi["p"], "theta": multi["theta"],
                    "variance_reduction_pct": multi["variance_reduction_pct"],
                    "covariates": covariate_keys,
                    "mode": "multi",
                }
                return result
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

    async def latest_look(self, experiment_id: str) -> dict | None:
        """Round 87 (scorecard parity): the most recent full-analysis look —
        the detail page's standing summary. Reads the audit trail only; None
        when no analysis has ever run."""
        event = (
            await self.db.execute(
                select(ExperimentEvent)
                .where(
                    ExperimentEvent.experiment_id == experiment_id,
                    ExperimentEvent.event_type == "analysis_look",
                )
                .order_by(ExperimentEvent.created_at.desc(),
                          ExperimentEvent.id.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if event is None:
            return None
        payload = event.payload or {}
        return {
            "at": payload.get("at"),
            "sequential": payload.get("sequential"),
            "look": payload.get("look"),
            "result_hash": payload.get("result_hash"),
            "warnings": payload.get("warnings", []),
            "primary_effects": payload.get("primary_effects", {}),
            "automated": event.actor_user_id is None,
        }

    async def look_history(
        self, experiment_id: str, *, limit: int = 50
    ) -> list[dict]:
        """Round 137: every recorded look, newest first — the audit-trail
        view the scorecard's latest row summarizes. Same shape as
        latest_look per entry."""
        events = list(
            (
                await self.db.execute(
                    select(ExperimentEvent)
                    .where(
                        ExperimentEvent.experiment_id == experiment_id,
                        ExperimentEvent.event_type == "analysis_look",
                    )
                    .order_by(ExperimentEvent.created_at.desc(),
                              ExperimentEvent.id.desc())
                    .limit(limit)
                )
            ).scalars()
        )
        return [
            {
                "at": (event.payload or {}).get("at"),
                "warnings": (event.payload or {}).get("warnings", []),
                "sequential": (event.payload or {}).get("sequential"),
                "look": (event.payload or {}).get("look"),
                "result_hash": (event.payload or {}).get("result_hash"),
                "primary_effects": (event.payload or {}).get("primary_effects", {}),
                "automated": event.actor_user_id is None,
            }
            for event in events
        ]

    async def run(
        self, experiment_id: str, *, actor: User, segment: str | None = None
    ) -> dict:
        """segment (§4.8): analyze one breakdown slice ('org:<id>'). Segment
        analyses are informational — they consume NO sequential look budget,
        record NO analysis_look event (so a decision can never reference
        them), and skip the corpus/bandit/novelty extras."""
        if segment is None:
            # Defect #48: the look budget is read-count-then-insert — two
            # concurrent full analyses both saw used=N, both passed the
            # max_looks gate and both recorded a look: the budget could be
            # EXCEEDED by one (alpha overspend beyond the O'Brien-Fleming
            # spending plan). The experiment row lock serializes full
            # analyses; informational segment slices stay lock-free (they
            # record no look).
            from app.experiments.services.experiments import ExperimentService

            exp = await ExperimentService(self.db)._get_locked(  # noqa: SLF001
                experiment_id
            )
        else:
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
        if segment is None and spec.sequential == "obrien_fleming":
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
                        MetricSnapshot.segment == "",
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
                aggregated, mixed = await self._aggregate_metric(
                    experiment_id, key, segment=segment or ""
                )
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
                # §4.6b (round 202): the "auto" spec selects covariates per
                # metric from the STORED aggregates (pooled |r| >= 0.1, at
                # most 3, deterministic). Selection is never silent: chosen
                # keys ride the cuped block and the run warns
                # CUPED_AUTO_SELECTED; nothing qualifying warns
                # CUPED_AUTO_NONE and degrades to plain Welch.
                cuped_auto = (
                    spec.variance_reduction is not None
                    and spec.variance_reduction.covariates() == ["auto"]
                )
                if cuped_auto:
                    from app.experiments.services.metrics import (
                        resolve_covariates,
                    )

                    def _y_arm(a: dict, kind: str = kind) -> dict:
                        if kind in ("binary", "time_to_event"):
                            y = a.get("numerator") or 0.0
                            return {"n": a.get("denominator") or 0.0,
                                    "sum": y, "sum_sq": y,
                                    "covariates": a.get("covariates")}
                        return {"n": a.get("n") or 0.0,
                                "sum": a.get("sum_value") or 0.0,
                                "sum_sq": a.get("sum_sq") or 0.0,
                                "covariates": a.get("covariates")}

                    chosen = stats.auto_select_covariates(
                        [_y_arm(a) for a in aggregated.values()],
                        resolve_covariates(spec.variance_reduction),
                    )
                    metric_covariate_keys = (
                        [c["key"] for c in chosen] or None
                    )
                    if chosen:
                        # the selection's evidence is part of the result —
                        # operators see WHY each covariate was chosen
                        entry["cuped_auto"] = {
                            c["key"]: c["r"] for c in chosen
                        }
                    flag = ("CUPED_AUTO_SELECTED" if metric_covariate_keys
                            else "CUPED_AUTO_NONE")
                    if flag not in warnings:
                        warnings.append(flag)
                else:
                    metric_covariate_keys = (
                        spec.variance_reduction.covariates()
                        if spec.variance_reduction is not None
                        else None
                    )
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
                        kind, spec.stats_engine, aggregated[control_key], arm,
                        covariate_keys=metric_covariate_keys,
                        auto=cuped_auto,
                    )
                    # §4.14 (round 124): quantile reads for continuous
                    # metrics whose definition requests them — informational,
                    # never a decision basis (the registered engine's primary
                    # comparison stays authoritative)
                    q_probs = (
                        (definition.spec or {}).get("quantiles")
                        if definition is not None and kind == "continuous"
                        else None
                    )
                    if q_probs:
                        q_out = {}
                        for prob in q_probs:
                            q_cmp = stats.quantile_comparison(
                                control_arm.get("value_histogram") or {},
                                arm.get("value_histogram") or {},
                                float(prob),
                            )
                            if q_cmp is not None:
                                q_out[str(prob)] = q_cmp
                        if q_out:
                            comparison["quantiles"] = q_out
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

        if segment is not None:
            payload = {
                "experiment_id": experiment_id,
                "experiment_key": exp.key,
                "segment": segment,
                "engine": spec.stats_engine,
                "analysis_type": spec.analysis_type,
                "causal_claim": False,
                "caveat": "Segment breakdown — informational slice, no decision basis.",
                "control": control_key,
                "metrics": metrics_out,
                "warnings": warnings,
            }
            payload["result_hash"] = result_hash(
                {k: payload[k] for k in ("metrics", "engine", "analysis_type", "control")}
            )
            return payload

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
            if actor.role != UserRole.ADMIN:
                # information boundary (§18): the corpus prior aggregates
                # effects across the whole domain, including other orgs'
                # experiments — platform-admin eyes only; delegated analyses
                # simply run without the shrinkage context
                break
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

        # Data-flow health (round 51): a RUNNING experiment whose newest
        # exposure is older than 48h (or that has none at all) is most often
        # a broken integration, not a finished experiment — surface it.
        if exp.status == "running":
            from app.experiments.models import ExperimentExposure

            last_exposure = (
                await self.db.execute(
                    select(func.max(ExperimentExposure.occurred_at)).where(
                        ExperimentExposure.experiment_id == experiment_id
                    )
                )
            ).scalar_one_or_none()
            stale_cutoff = datetime.now(UTC) - timedelta(hours=48)
            if last_exposure is None or (
                (last_exposure.replace(tzinfo=UTC) if last_exposure.tzinfo is None
                 else last_exposure) < stale_cutoff
            ):
                warnings.append("NO_RECENT_EXPOSURES")

        # Design-time power vs reality (§4.13 v3): when the spec declares a
        # power target, compute the required n per arm from the OBSERVED
        # control baseline of the first binary primary metric and compare it
        # with the smallest arm. An underpowered read gets a health warning —
        # a "no effect" conclusion below the target is not evidence of
        # absence.
        power_block = None
        if spec.power is not None:
            for key in spec.metrics.primary:
                entry = metrics_out.get(key)
                # binary AND rate are both proportion-shaped (numerator /
                # denominator) — the two-proportion formula applies to both
                if not entry or entry.get("kind") not in ("binary", "rate"):
                    continue
                aggregated, _ = await self._aggregate_metric(
                    experiment_id, key, segment=segment or ""
                )
                control_arm = aggregated.get(control_key)
                if not control_arm or not control_arm.get("denominator"):
                    continue
                baseline = control_arm["numerator"] / control_arm["denominator"]
                required = stats.required_n_per_arm(
                    baseline, spec.power.mde,
                    alpha=spec.power.alpha, power=spec.power.power,
                )
                if required is None:
                    continue
                min_arm_n = min(
                    int(arm.get("denominator") or 0) for arm in aggregated.values()
                )
                power_block = {
                    "metric_key": key,
                    "baseline_rate": baseline,
                    "mde": spec.power.mde,
                    "alpha": spec.power.alpha,
                    "power": spec.power.power,
                    "required_n_per_arm": required,
                    "min_arm_n": min_arm_n,
                    "powered": min_arm_n >= required,
                }
                if min_arm_n < required:
                    warnings.append("SAMPLE_BELOW_POWER_TARGET")
                break

        # §4.15 (round 182): Kaplan-Meier at the horizon for time_to_event
        # primaries whose definition opts in (spec.km) — counts computed ON
        # DEMAND (cumulative-from-assignment does not fit additive snapshot
        # folds). The horizon reads the DB clock (#68 law: event rows
        # timestamp with server_default now()).
        # The event reader below is PLACEMENT-based, so only talent_outcomes
        # definitions qualify — a billing time_to_event (retention_rate)
        # opting in would otherwise get placement curves attached to a
        # billing metric (round 188). Honest refusal: warn, don't attach.
        km_keys = []
        for key in spec.metrics.primary:
            definition = definitions.get(key)
            if (definition is None or definition.kind != "time_to_event"
                    or not (definition.spec or {}).get("km")):
                continue
            if (definition.spec or {}).get("source") != "talent_outcomes":
                if "KM_SOURCE_UNSUPPORTED" not in warnings:
                    warnings.append("KM_SOURCE_UNSUPPORTED")
                continue
            km_keys.append(key)
        if km_keys:
            from sqlalchemy import func as _func

            from app.experiments.models import ExperimentAssignment
            from app.talent.models.application import Placement

            horizon = (
                await self.db.execute(select(_func.clock_timestamp()))
            ).scalar_one()
            if horizon.tzinfo is None:
                horizon = horizon.replace(tzinfo=UTC)
            rows = (
                await self.db.execute(
                    select(
                        ExperimentAssignment.variant_key,
                        ExperimentAssignment.unit_id,
                        ExperimentAssignment.assigned_at,
                    ).where(
                        ExperimentAssignment.experiment_id == experiment_id,
                        ExperimentAssignment.is_holdout.is_(False),
                    )
                )
            ).all()
            by_arm: dict[str, list] = {}
            for variant_key, unit_id, assigned_at in rows:
                if assigned_at.tzinfo is None:
                    assigned_at = assigned_at.replace(tzinfo=UTC)
                by_arm.setdefault(variant_key, []).append((unit_id, assigned_at))
            all_unit_ids = [u for arm in by_arm.values() for u, _ in arm]
            first_event: dict[str, object] = {}
            if all_unit_ids:
                event_rows = (
                    await self.db.execute(
                        select(
                            Placement.user_id,
                            _func.min(Placement.created_at),
                        )
                        .where(
                            Placement.user_id.in_(all_unit_ids),
                            Placement.status != "cancelled",
                        )
                        .group_by(Placement.user_id)
                    )
                ).all()
                first_event = dict(event_rows)
            for key in km_keys:
                curves = {}
                for variant_key, members in by_arm.items():
                    events: dict[int, int] = {}
                    censored: dict[int, int] = {}
                    for unit_id, assigned_at in members:
                        placed = first_event.get(unit_id)
                        if placed is not None and placed.tzinfo is None:
                            placed = placed.replace(tzinfo=UTC)
                        if placed is not None and placed >= assigned_at:
                            day = (placed - assigned_at).days
                            events[day] = events.get(day, 0) + 1
                        else:
                            day = max((horizon - assigned_at).days, 0)
                            censored[day] = censored.get(day, 0) + 1
                    curves[variant_key] = stats.km_curve(
                        events, censored, len(members)
                    )
                km_cmp = stats.km_compare(
                    curves.get(control_key),
                    next((c for v, c in curves.items() if v != control_key),
                         None),
                )
                if km_cmp is not None and key in metrics_out:
                    metrics_out[key]["km"] = km_cmp

        if spec.analysis_type == "observational" and exp.started_at is not None:
            # §10 v3 (round 178): INTERRUPTED TIME SERIES over on-demand
            # daily source reads — "no pre-period" only meant no pre-period
            # snapshots; the sources accept arbitrary windows. Whole-roster
            # daily means (ITS has no concurrent control), ITS_DAYS per
            # side, segmented OLS in the pure core. Association only.
            from app.experiments.services.metrics import MetricService

            its_roster = await MetricService(self.db)._variant_units(  # noqa: SLF001
                experiment_id
            )
            all_units = sorted({u for us in its_roster.values() for u in us})
            if all_units:
                from app.experiments.services.metrics import SOURCE_REGISTRY

                start_day = exp.started_at.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                for key in spec.metrics.primary[:1]:
                    definition = definitions.get(key)
                    source = (
                        SOURCE_REGISTRY.get(definition.spec.get("source", ""))
                        if definition is not None
                        else None
                    )
                    if source is None:
                        continue

                    async def _daily_mean(day_start):
                        stats_out = await source(  # noqa: B023
                            self.db,
                            experiment=exp,
                            definition=definition,  # noqa: B023
                            variant_units={"all": all_units},
                            window_start=day_start,
                            window_end=day_start + timedelta(days=1),
                            unit_type=spec.unit_type,
                        )
                        arm = stats_out.get("all") or {}
                        if arm.get("denominator"):
                            return float(arm.get("numerator") or 0.0) / float(
                                arm["denominator"]
                            )
                        if arm.get("n"):
                            return float(arm.get("sum_value") or 0.0) / float(
                                arm["n"]
                            )
                        return None

                    pre_series: list[float] = []
                    post_series: list[float] = []
                    for offset in range(ITS_DAYS, 0, -1):
                        value = await _daily_mean(
                            start_day - timedelta(days=offset)
                        )
                        pre_series.append(0.0 if value is None else value)
                    for offset in range(ITS_DAYS):
                        value = await _daily_mean(
                            start_day + timedelta(days=offset)
                        )
                        post_series.append(0.0 if value is None else value)
                    its = stats.its_estimate(pre_series, post_series)
                    if its is not None and key in metrics_out:
                        metrics_out[key]["its"] = its

                    # §4.16 (round 195): SYNTHETIC CONTROL over the same
                    # daily windows — donor pool = control-arm units (capped,
                    # sorted for determinism), treated series = mean over the
                    # other arms' units, one source call per day with the
                    # per-unit variant_units fan-out.
                    donor_units = sorted(
                        its_roster.get(control_key, [])
                    )[:SC_MAX_DONORS]
                    treated_units = sorted(
                        u for v, us in its_roster.items()
                        if v != control_key for u in us
                    )
                    if len(donor_units) < 2 or not treated_units:
                        if "SC_DONOR_POOL_SMALL" not in warnings:
                            warnings.append("SC_DONOR_POOL_SMALL")
                        continue
                    sc_units = [*donor_units, *treated_units]
                    per_unit: dict[str, tuple[list, list]] = {
                        u: ([], []) for u in sc_units
                    }

                    async def _daily_per_unit(day_start, side):
                        stats_out = await source(  # noqa: B023
                            self.db,
                            experiment=exp,
                            definition=definition,  # noqa: B023
                            variant_units={u: [u] for u in per_unit},  # noqa: B023
                            window_start=day_start,
                            window_end=day_start + timedelta(days=1),
                            unit_type=spec.unit_type,
                        )
                        for u, series in per_unit.items():  # noqa: B023
                            arm = stats_out.get(u) or {}
                            if arm.get("denominator"):
                                val = (float(arm.get("numerator") or 0.0)
                                       / float(arm["denominator"]))
                            elif arm.get("n"):
                                val = (float(arm.get("sum_value") or 0.0)
                                       / float(arm["n"]))
                            else:
                                val = 0.0
                            series[side].append(val)

                    for offset in range(ITS_DAYS, 0, -1):
                        await _daily_per_unit(
                            start_day - timedelta(days=offset), 0
                        )
                    for offset in range(ITS_DAYS):
                        await _daily_per_unit(
                            start_day + timedelta(days=offset), 1
                        )
                    n_t = len(treated_units)
                    pre_treated = [
                        sum(per_unit[u][0][t] for u in treated_units) / n_t
                        for t in range(ITS_DAYS)
                    ]
                    post_treated = [
                        sum(per_unit[u][1][t] for u in treated_units) / n_t
                        for t in range(ITS_DAYS)
                    ]
                    sc = stats.synthetic_control(
                        pre_treated, post_treated,
                        [per_unit[u][0] for u in donor_units],
                        [per_unit[u][1] for u in donor_units],
                    )
                    if sc is not None and key in metrics_out:
                        metrics_out[key]["synthetic_control"] = sc

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
                # round 247: a RATE-kind primary is the one kind the CUPED
                # cores deliberately do not adjust (ratio metrics need a
                # delta-method treatment, §4.6 boundary) — say THAT, not the
                # misleading "sources computed nothing"
                rate_primary = any(
                    (metrics_out.get(key) or {}).get("kind") == "rate"
                    for key in spec.metrics.primary
                )
                if rate_primary:
                    if "CUPED_RATE_UNSUPPORTED" not in warnings:
                        warnings.append("CUPED_RATE_UNSUPPORTED")
                # Configured but no source computed covariate aggregates yet
                # (auto-none already explains itself — no double bark)
                elif "CUPED_AUTO_NONE" not in warnings:
                    warnings.append("CUPED_COVARIATES_UNAVAILABLE")
            elif len(spec.variance_reduction.covariates()) > 1 and not any(
                (comparison.get("cuped") or {}).get("mode") == "multi"
                for metric in metrics_out.values()
                for comparison in (metric.get("comparisons") or {}).values()
            ):
                # #62: a multi-covariate spec fell back to the single-covariate
                # adjustment (a covariate's source has no provider, or the
                # joint design was degenerate) — the operator asked for a
                # joint adjustment and must not mistake this for one
                warnings.append("CUPED_MULTI_DEGRADED")

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
        if power_block is not None:
            payload["power"] = power_block
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
                    # round 234: the look's WARNINGS ride the audit trail —
                    # a decision that cites this hash can show its caveats
                    "warnings": payload.get("warnings", []),
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
