"""Metric snapshot computation with provenance (ADR-017 §4.6–§4.7, §8).

ITT discipline: units are grouped by ASSIGNED variant regardless of later
behavior; holdout assignments are excluded from variant aggregates. Windows
are UTC days. Recomputation is an UPSERT on the window's unique key — the
provenance JSONB records the query_version and row counts of every compute.

Metric sources are a registry: a source callable receives the ITT unit sets
and returns per-variant sufficient statistics. Unknown sources are SKIPPED
(logged) — a definition may land before its integration phase wires the
source (exp07).
"""

import math
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models import (
    Experiment,
    ExperimentAssignment,
    ExperimentExposure,
    ExperimentVersion,
)
from app.experiments.models.metric import (
    METRIC_DIRECTIONS,
    METRIC_KINDS,
    METRIC_PRIVACY_CLASSES,
    METRIC_SOURCE_KINDS,
    MetricDefinition,
    MetricSnapshot,
)
from app.experiments.schemas import ExperimentSpec

log = structlog.get_logger()

# variant_key -> sufficient stats dict (subset of MetricSnapshot columns)
SourceResult = dict[str, dict]
SourceFn = Callable[..., Awaitable[SourceResult]]

SOURCE_REGISTRY: dict[str, SourceFn] = {}


def register_source(name: str):
    def wrap(fn: SourceFn) -> SourceFn:
        SOURCE_REGISTRY[name] = fn
        return fn

    return wrap


# ── §4.6 v3 multi-covariate CUPED (round 114) ────────────────────────
# A covariate PROVIDER returns per-unit pre-period values for one metric
# key over user units. Providers are registered per source; cross-source
# covariates work for any (main metric, covariate) pair whose covariate
# source has a provider. k == 1 keeps the legacy in-source path untouched.

def value_histogram(values: list[float]) -> dict:
    """§4.14 (round 124): base-2 log histogram {bucket: count} over positive
    values, with "__zero__"/"__neg__" overflow keys. Mergeable across
    windows/segments by plain addition; ~2 significant digits of relative
    precision — enough for a p95 regression read."""
    hist: dict = {}
    for v in values:
        if v < 0:
            key = "__neg__"
        elif v == 0:
            key = "__zero__"
        else:
            key = str(max(-20, min(43, math.floor(math.log2(v)))))
        hist[key] = hist.get(key, 0) + 1
    return hist


def _validate_quantiles(quantiles, kind) -> None:
    """§4.14: 1-3 probabilities strictly inside (0, 1), continuous-kind
    definitions only (quantiles of a binary/rate are not a thing here)."""
    if quantiles is None:
        return
    if not isinstance(quantiles, (list, tuple)) or not 1 <= len(quantiles) <= 3:
        raise AppError(
            "VALIDATION_ERROR", "quantiles must list 1-3 probabilities", 422
        )
    for value in quantiles:
        if not isinstance(value, (int, float)) or not 0.0 < float(value) < 1.0:
            raise AppError(
                "VALIDATION_ERROR",
                f"quantile {value!r} outside (0, 1)",
                422,
            )
    if kind != "continuous":
        raise AppError(
            "VALIDATION_ERROR",
            f"quantiles require a continuous metric (kind: {kind})",
            422,
        )


COVARIATE_PROVIDERS: dict = {}

# §4.6b (round 202): the reserved "auto" covariate spec folds every
# provider's CANONICAL covariate so analysis-time selection has all the
# candidates in the stored aggregates
AUTO_COVARIATE_DEFAULTS = {
    "projects": "revision_count",
    "evaluations": "practical_pass_rate",
}


def resolve_covariates(variance_reduction) -> list[str]:
    keys = variance_reduction.covariates()
    if keys == ["auto"]:
        return sorted(AUTO_COVARIATE_DEFAULTS.values())
    return keys


def covariate_provider(source_name: str):
    def wrap(fn):
        COVARIATE_PROVIDERS[source_name] = fn
        return fn

    return wrap


@covariate_provider("projects")
async def _cov_projects(
    db: AsyncSession, *, definition, units: list[str],
    lookback_start, window_start,
) -> dict[str, float]:
    from app.models.project import Submission

    rows = (
        await db.execute(
            select(Submission.user_id, Submission.version).where(
                Submission.user_id.in_(units),
                Submission.created_at >= lookback_start,
                Submission.created_at < window_start,
            )
        )
    ).all()
    x: dict[str, float] = dict.fromkeys(units, 0.0)
    measure = (definition.spec or {}).get("measure", "approval_rate")
    if measure == "revision_count":
        for user_id, version in rows:
            x[user_id] += float(max(0, version - 1))
        return x
    # approval_rate (and any count-like measure): approved submissions per
    # unit in the lookback — needs the status column
    from app.models.project import SubmissionStatus

    status_rows = (
        await db.execute(
            select(Submission.user_id, Submission.status).where(
                Submission.user_id.in_(units),
                Submission.created_at >= lookback_start,
                Submission.created_at < window_start,
            )
        )
    ).all()
    x = dict.fromkeys(units, 0.0)
    for user_id, status in status_rows:
        if status == SubmissionStatus.APPROVED:
            x[user_id] += 1.0
    return x


@covariate_provider("evaluations")
async def _cov_evaluations(
    db: AsyncSession, *, definition, units: list[str],
    lookback_start, window_start,
) -> dict[str, float]:
    """Pre-period review outcomes per user unit (round 117): mirrors the
    evaluations SOURCE semantics (SubmissionReview verdicts, ADR-006/008).
    Measures: pass_count (default — APPROVED reviews) or review_count."""
    from app.models.project import ReviewStatus, Submission, SubmissionReview

    rows = (
        await db.execute(
            select(Submission.user_id, SubmissionReview.status)
            .join(Submission, Submission.id == SubmissionReview.submission_id)
            .where(
                Submission.user_id.in_(units),
                SubmissionReview.created_at >= lookback_start,
                SubmissionReview.created_at < window_start,
            )
        )
    ).all()
    measure = (definition.spec or {}).get("measure", "pass_count")
    x: dict[str, float] = dict.fromkeys(units, 0.0)
    for user_id, status in rows:
        if measure == "review_count" or status == ReviewStatus.APPROVED:
            x[user_id] += 1.0
    return x


async def assemble_covariates(
    db: AsyncSession, *, variance_reduction, definitions_by_key: dict,
    unit_values: dict[str, float], window_start,
) -> dict:
    """Build the exp12 covariates map {key: {sum, sum_sq, xy_sum}} from each
    covariate's provider; units with no pre-period data count as zero (ITT).
    A covariate whose source has no provider is skipped (recorded upstream
    as CUPED_COVARIATES_UNAVAILABLE by the analysis warning)."""
    from datetime import timedelta

    units = list(unit_values.keys())
    lookback_start = window_start - timedelta(
        days=variance_reduction.lookback_days
    )
    out: dict = {}
    x_maps: dict[str, dict[str, float]] = {}
    for cov_key in resolve_covariates(variance_reduction):
        definition = definitions_by_key.get(cov_key)
        if definition is None:
            # covariates need not appear among the spec's metrics — fetch
            definition = (
                await db.execute(
                    select(MetricDefinition).where(MetricDefinition.key == cov_key)
                )
            ).scalar_one_or_none()
        provider = (
            COVARIATE_PROVIDERS.get((definition.spec or {}).get("source", ""))
            if definition is not None
            else None
        )
        if provider is None:
            continue
        x = await provider(
            db, definition=definition, units=units,
            lookback_start=lookback_start, window_start=window_start,
        )
        xs = [x.get(u, 0.0) for u in units]
        ys = [unit_values[u] for u in units]
        out[cov_key] = {
            "sum": sum(xs),
            "sum_sq": sum(v * v for v in xs),
            "xy_sum": sum(a * b for a, b in zip(ys, xs, strict=True)),
        }
        x_maps[cov_key] = x
    # §4.6 v3 step 3 needs the covariate CROSS-products for the joint OLS —
    # upper triangle only, keyed on the earlier covariate
    keys = [k for k in resolve_covariates(variance_reduction) if k in out]
    for i, ki in enumerate(keys):
        xx: dict[str, float] = {}
        for kj in keys[i + 1:]:
            xi, xj = x_maps[ki], x_maps[kj]
            xx[kj] = sum(xi.get(u, 0.0) * xj.get(u, 0.0) for u in units)
        if xx:
            out[ki]["xx"] = xx
    return out


def winsorize(values: list[float], pct) -> tuple[list[float], bool]:
    """Clamp the upper tail at the empirical pct-th percentile (v2 §4.6).
    Returns (values, applied) — provenance records the adjustment only when
    it actually happened. A pct of None (or <2 samples) is a no-op."""
    if pct is None or len(values) < 2:
        return values, False
    import math

    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil(len(ordered) * float(pct) / 100.0) - 1))
    cap = ordered[idx]
    return [min(v, cap) for v in values], True


# ── Built-in sources ─────────────────────────────────────────────────


@register_source("exposures")
async def _source_exposures(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Exposure rate per variant: numerator = DISTINCT exposed units in the
    window (a unit hitting the surface five times is one exposed unit — a raw
    event count pushes the rate past 1.0 and false-fires lte guardrails),
    denominator = assigned units (ITT). Fully internal — always available."""
    q = (
        select(ExperimentAssignment.variant_key, ExperimentAssignment.unit_id)
        .join(ExperimentExposure, ExperimentExposure.assignment_id == ExperimentAssignment.id)
        .where(
            ExperimentExposure.experiment_id == experiment.id,
            ExperimentExposure.occurred_at >= window_start,
            ExperimentExposure.occurred_at < window_end,
            ExperimentAssignment.is_holdout.is_(False),
        )
        .distinct()
    )
    exposed: dict[str, set[str]] = {}
    for variant_key, unit_id in (await db.execute(q)).all():
        exposed.setdefault(variant_key, set()).add(unit_id)
    # Switchback (§4.5): assignment rows carry the placeholder variant —
    # exposures in the window belong to the variant that owned the window
    # (the single key compute passes in)
    from app.experiments.services.assignment import SWITCHBACK_PLACEHOLDER

    placeholder_units = exposed.pop(SWITCHBACK_PLACEHOLDER, None)
    if placeholder_units is not None and len(variant_units) == 1:
        only = next(iter(variant_units))
        exposed[only] = exposed.get(only, set()) | placeholder_units
    # Numerators are intersected with the POPULATION each variant was called
    # with (defect #31): segment slices and exposed-only rosters pass a
    # subset — counting all exposed units overstated every slice's numerator
    return {
        variant: {
            "n": len(units),
            "numerator": len(exposed.get(variant, set()) & set(units)),
            "denominator": len(units),
        }
        for variant, units in variant_units.items()
    }


@register_source("workflow_runs")
async def _source_workflow_runs(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Production metrics over WorkflowRun for workflow_installation units.

    measure=success_rate → binary (numerator completed / denominator terminal)
    measure=latency_ms   → continuous (sum, sum_sq over run durations)
    """
    from app.models.workflow_run import RunStatus, WorkflowRun

    measure = definition.spec.get("measure", "success_rate")
    terminal = (RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED)
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units:
            result[variant] = {"n": 0}
            continue
        rows = (
            await db.execute(
                select(WorkflowRun.status, WorkflowRun.started_at, WorkflowRun.finished_at).where(
                    WorkflowRun.installation_id.in_(units),
                    WorkflowRun.created_at >= window_start,
                    WorkflowRun.created_at < window_end,
                    WorkflowRun.status.in_(terminal),
                )
            )
        ).all()
        if measure == "latency_ms":
            if (
                variance_reduction is not None
                and definition.key in variance_reduction.covariates()
            ):
                # CUPED mode (§4.6 v2, third source on the shared contract):
                # per-UNIT mean latency — y over the window, x over the
                # pre-window lookback; ITT zero-fill for silent installations
                lookback_start = window_start - timedelta(
                    days=variance_reduction.lookback_days
                )

                async def _unit_latency(start, end, units=units):
                    period_rows = (
                        await db.execute(
                            select(
                                WorkflowRun.installation_id,
                                WorkflowRun.started_at,
                                WorkflowRun.finished_at,
                            ).where(
                                WorkflowRun.installation_id.in_(units),
                                WorkflowRun.created_at >= start,
                                WorkflowRun.created_at < end,
                                WorkflowRun.status.in_(terminal),
                            )
                        )
                    ).all()
                    per_unit: dict[str, list[float]] = {}
                    for installation_id, started, finished in period_rows:
                        if started is None or finished is None:
                            continue
                        per_unit.setdefault(installation_id, []).append(
                            (finished - started).total_seconds() * 1000.0
                        )
                    return {
                        u: sum(vals) / len(vals) for u, vals in per_unit.items()
                    }

                cur = await _unit_latency(window_start, window_end)
                pre = await _unit_latency(lookback_start, window_start)
                ys = [cur.get(u, 0.0) for u in units]
                xs = [pre.get(u, 0.0) for u in units]
                ys, winsorized = winsorize(ys, definition.winsorize_pct)
                result[variant] = {
                    "n": len(units),
                    "sum_value": sum(ys),
                    "sum_sq": sum(v * v for v in ys),
                    "cov_sum": sum(xs),
                    "cov_sum_sq": sum(v * v for v in xs),
                    "cov_xy_sum": sum(a * b for a, b in zip(ys, xs, strict=True)),
                    "_winsorized": winsorized,
                    "_aggregation": "per_unit",
                }
                continue
            durations = [
                (finished - started).total_seconds() * 1000.0
                for status, started, finished in rows
                if started is not None and finished is not None
            ]
            cap = float(definition.cap_value) if definition.cap_value is not None else None
            if cap is not None:
                durations = [min(d, cap) for d in durations]
            durations, winsorized = winsorize(durations, definition.winsorize_pct)
            result[variant] = {
                "n": len(durations),
                "sum_value": sum(durations),
                "sum_sq": sum(d * d for d in durations),
                "_winsorized": winsorized,
            }
            # §4.14: per-event sketch ONLY when the definition asks for
            # quantiles — no silent write amplification
            if definition.spec.get("quantiles"):
                result[variant]["value_histogram"] = value_histogram(durations)
        elif measure == "failure_rate":
            failed = sum(1 for status, _s, _f in rows if status == RunStatus.FAILED)
            result[variant] = {
                "n": len(rows),
                "numerator": failed,
                "denominator": len(rows),
            }
        else:
            completed = sum(1 for status, _s, _f in rows if status == RunStatus.COMPLETED)
            result[variant] = {
                "n": len(rows),
                "numerator": completed,
                "denominator": len(rows),
            }
    return result


@register_source("projects")
async def _source_projects(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Learning outcomes over Submission (user units).

    measure=approval_rate  → binary: approved / all submissions in window
    measure=revision_count → continuous: per-submission (version - 1)
    """
    from app.models.project import Submission, SubmissionStatus

    if unit_type != "user":
        return {variant: {"n": 0} for variant in variant_units}
    measure = definition.spec.get("measure", "approval_rate")
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units:
            result[variant] = {"n": 0}
            continue
        rows = (
            await db.execute(
                select(Submission.status, Submission.version).where(
                    Submission.user_id.in_(units),
                    Submission.created_at >= window_start,
                    Submission.created_at < window_end,
                )
            )
        ).all()
        if measure == "revision_count":
            if (
                variance_reduction is not None
                and len(variance_reduction.covariates()) > 1
            ):
                # §4.6 v3 (round 114): multi-covariate mode — the source
                # emits per-unit y only; the assembler computes EVERY
                # covariate's x through its provider (cross-source capable)
                cur_rows = (
                    await db.execute(
                        select(Submission.user_id, Submission.version).where(
                            Submission.user_id.in_(units),
                            Submission.created_at >= window_start,
                            Submission.created_at < window_end,
                        )
                    )
                ).all()
                y: dict[str, float] = dict.fromkeys(units, 0.0)
                for user_id, version in cur_rows:
                    y[user_id] += float(max(0, version - 1))
                # round 157 (the wave-24 ledger's design note repaid): the
                # multi branch now winsorizes y like the single branch —
                # a robustness knob must apply identically on both paths.
                # The winsorized values flow into BOTH the sums and the
                # per-unit map the assembler pairs with covariates.
                ys, winsorized = winsorize(
                    [y[u] for u in units], definition.winsorize_pct
                )
                y = dict(zip(units, ys, strict=True))
                result[variant] = {
                    "n": len(units),
                    "sum_value": sum(ys),
                    "sum_sq": sum(v * v for v in ys),
                    "_aggregation": "per_unit",
                    "_unit_values": y,
                    "_winsorized": winsorized,
                }
                continue
            if (
                variance_reduction is not None
                and definition.key in variance_reduction.covariates()
            ):
                # CUPED mode (§4.6 v2): per-UNIT aggregation so each unit
                # contributes one (y, x) pair — y = revisions in the window,
                # x = revisions in the pre-assignment lookback of the SAME
                # metric. Every assigned unit counts (ITT, zero when silent);
                # NOTE the n/unit-of-analysis change vs per-submission mode.
                lookback_start = window_start - timedelta(
                    days=variance_reduction.lookback_days
                )
                pre_rows = (
                    await db.execute(
                        select(Submission.user_id, Submission.version).where(
                            Submission.user_id.in_(units),
                            Submission.created_at >= lookback_start,
                            Submission.created_at < window_start,
                        )
                    )
                ).all()
                cur_rows = (
                    await db.execute(
                        select(Submission.user_id, Submission.version).where(
                            Submission.user_id.in_(units),
                            Submission.created_at >= window_start,
                            Submission.created_at < window_end,
                        )
                    )
                ).all()
                y: dict[str, float] = dict.fromkeys(units, 0.0)
                x: dict[str, float] = dict.fromkeys(units, 0.0)
                for user_id, version in cur_rows:
                    y[user_id] += float(max(0, version - 1))
                for user_id, version in pre_rows:
                    x[user_id] += float(max(0, version - 1))
                ys, winsorized = winsorize([y[u] for u in units], definition.winsorize_pct)
                xs = [x[u] for u in units]
                result[variant] = {
                    "n": len(units),
                    "sum_value": sum(ys),
                    "sum_sq": sum(v * v for v in ys),
                    "cov_sum": sum(xs),
                    "cov_sum_sq": sum(v * v for v in xs),
                    "cov_xy_sum": sum(a * b for a, b in zip(ys, xs, strict=True)),
                    "_winsorized": winsorized,
                    "_aggregation": "per_unit",
                }
                continue
            revisions = [float(max(0, version - 1)) for _status, version in rows]
            revisions, winsorized = winsorize(revisions, definition.winsorize_pct)
            result[variant] = {
                "n": len(revisions),
                "sum_value": sum(revisions),
                "sum_sq": sum(r * r for r in revisions),
                "_winsorized": winsorized,
            }
        else:
            if (
                variance_reduction is not None
                and definition.key not in variance_reduction.covariates()
            ):
                # Binary CUPED (round 142, Statsig-parity regression
                # adjustment on proportions): per-UNIT y — 1 when the unit
                # landed an APPROVED submission in the window, 0 otherwise
                # (ITT; NOTE the unit-of-analysis change vs per-submission
                # mode, same contract as the revision_count CUPED branch).
                # The assembler builds every covariate from its provider and
                # the analysis reuses the Welch CUPED core on the 0/1 y.
                cur_rows = (
                    await db.execute(
                        select(Submission.user_id, Submission.status).where(
                            Submission.user_id.in_(units),
                            Submission.created_at >= window_start,
                            Submission.created_at < window_end,
                        )
                    )
                ).all()
                y: dict[str, float] = dict.fromkeys(units, 0.0)
                for user_id, status in cur_rows:
                    if status == SubmissionStatus.APPROVED:
                        y[user_id] = 1.0
                approved_units = sum(1 for u in units if y[u] > 0)
                result[variant] = {
                    "n": len(units),
                    "numerator": approved_units,
                    "denominator": len(units),
                    "_aggregation": "per_unit",
                    "_unit_values": y,
                }
                continue
            approved = sum(1 for status, _v in rows if status == SubmissionStatus.APPROVED)
            result[variant] = {"n": len(rows), "numerator": approved, "denominator": len(rows)}
    return result


@register_source("cost_ledger")
async def _source_cost_ledger(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Internal cost (USD) from metered evaluation spend, per org/tenant
    units. Money stays Decimal→float at the aggregate boundary only."""
    from app.models.evaluation import EvaluationTask

    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units or unit_type not in ("organization", "tenant"):
            result[variant] = {"n": 0}
            continue
        if (
            variance_reduction is not None
            and definition.key in variance_reduction.covariates()
        ):
            # CUPED mode (§4.6 v2, same contract as projects): per-UNIT
            # totals — y = unit's cost in the window, x = its cost in the
            # pre-window lookback; every unit counts (ITT, zero when silent)
            lookback_start = window_start - timedelta(
                days=variance_reduction.lookback_days
            )

            async def _unit_costs(start, end, units=units):
                if unit_type == "organization":
                    q = (
                        select(EvaluationTask.org_id, func.sum(EvaluationTask.cost_usd))
                        .where(
                            EvaluationTask.cost_usd.is_not(None),
                            EvaluationTask.created_at >= start,
                            EvaluationTask.created_at < end,
                            EvaluationTask.org_id.in_(units),
                        )
                        .group_by(EvaluationTask.org_id)
                    )
                    return dict((await db.execute(q)).all())
                from app.models.organization import Organization

                q = (
                    select(Organization.tenant_id, func.sum(EvaluationTask.cost_usd))
                    .join(Organization, Organization.id == EvaluationTask.org_id)
                    .where(
                        EvaluationTask.cost_usd.is_not(None),
                        EvaluationTask.created_at >= start,
                        EvaluationTask.created_at < end,
                        Organization.tenant_id.in_(units),
                    )
                    .group_by(Organization.tenant_id)
                )
                return dict((await db.execute(q)).all())

            cur = await _unit_costs(window_start, window_end)
            pre = await _unit_costs(lookback_start, window_start)
            ys = [float(cur.get(u) or 0.0) for u in units]
            xs = [float(pre.get(u) or 0.0) for u in units]
            ys, winsorized = winsorize(ys, definition.winsorize_pct)
            result[variant] = {
                "n": len(units),
                "sum_value": sum(ys),
                "sum_sq": sum(v * v for v in ys),
                "cov_sum": sum(xs),
                "cov_sum_sq": sum(v * v for v in xs),
                "cov_xy_sum": sum(a * b for a, b in zip(ys, xs, strict=True)),
                "_winsorized": winsorized,
                "_aggregation": "per_unit",
            }
            continue
        q = select(EvaluationTask.cost_usd).where(
            EvaluationTask.cost_usd.is_not(None),
            EvaluationTask.created_at >= window_start,
            EvaluationTask.created_at < window_end,
        )
        if unit_type == "organization":
            q = q.where(EvaluationTask.org_id.in_(units))
        else:  # tenant units → their orgs
            from app.models.organization import Organization

            q = q.join(Organization, Organization.id == EvaluationTask.org_id).where(
                Organization.tenant_id.in_(units)
            )
        costs = [float(c) for (c,) in (await db.execute(q)).all()]
        costs, winsorized = winsorize(costs, definition.winsorize_pct)
        result[variant] = {
            "n": len(costs),
            "sum_value": sum(costs),
            "sum_sq": sum(c * c for c in costs),
            "_winsorized": winsorized,
        }
    return result


@register_source("client_briefs")
async def _source_client_briefs(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Client acceptance per org unit: COMPLETED (client accepted the
    deliverables) / all briefs touched in the window (updated_at —
    acceptance is a late transition)."""
    from app.models.client_brief import ClientBrief

    if unit_type != "organization":
        return {variant: {"n": 0} for variant in variant_units}
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units:
            result[variant] = {"n": 0}
            continue
        rows = (
            await db.execute(
                select(ClientBrief.status).where(
                    ClientBrief.org_id.in_(units),
                    ClientBrief.updated_at >= window_start,
                    ClientBrief.updated_at < window_end,
                )
            )
        ).all()
        accepted = sum(
            1 for (status,) in rows if getattr(status, "value", status) == "completed"
        )
        result[variant] = {"n": len(rows), "numerator": accepted, "denominator": len(rows)}
    return result


@register_source("registry")
async def _source_registry(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Pack adoption per org unit: installations created in the window over
    the org count (rate)."""
    from app.models.skill_pack import SkillPackInstallation

    if unit_type != "organization":
        return {variant: {"n": 0} for variant in variant_units}
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units:
            result[variant] = {"n": 0}
            continue
        installs = (
            await db.execute(
                select(func.count()).where(
                    SkillPackInstallation.org_id.in_(units),
                    SkillPackInstallation.installed_at >= window_start,
                    SkillPackInstallation.installed_at < window_end,
                )
            )
        ).scalar_one()
        result[variant] = {"n": len(units), "numerator": installs, "denominator": len(units)}
    return result


@register_source("eco_telemetry")
async def _source_eco_telemetry(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Provider reliability from eco TelemetrySnapshots (provider_offering
    units): sample-weighted success — numerator Σ(success_rate·samples),
    denominator Σ samples. Reads approved aggregates only (eco privacy
    thresholds already applied at snapshot time)."""
    from app.ecosystem.models.graph import TelemetrySnapshot

    if unit_type != "provider_offering":
        return {variant: {"n": 0} for variant in variant_units}
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units:
            result[variant] = {"n": 0}
            continue
        rows = (
            await db.execute(
                select(TelemetrySnapshot.sample_size, TelemetrySnapshot.metrics).where(
                    TelemetrySnapshot.entity_kind == "provider_offering",
                    TelemetrySnapshot.entity_id.in_(units),
                    TelemetrySnapshot.window_start >= window_start,
                    TelemetrySnapshot.window_start < window_end,
                )
            )
        ).all()
        weighted = 0.0
        samples = 0
        for sample_size, metrics in rows:
            rate = metrics.get("success_rate")
            if rate is None or not sample_size:
                continue
            weighted += float(rate) * sample_size
            samples += sample_size
        result[variant] = {"n": samples, "numerator": weighted, "denominator": samples}
    return result


# ── Seed definitions (Part C) ────────────────────────────────────────


@register_source("learning_paths")
async def _source_learning_paths(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Derived path completion over user units (no progress table — §18).

    A path counts as DERIVABLE when every required item is a PROJECT: its
    completion event for a user is the moment the last required project gets
    an approved submission (approval time ≈ the earliest approved
    submission's updated_at — the approval write bumps it). Paths with
    required skill/workflow items are excluded from BOTH sides (that scope
    is stamped in provenance via query_version; widening it is a
    query_version bump, not a silent change).

    completion_rate            binary: units with ≥1 completion in-window / units
    time_to_completion_hours   continuous: first-submission → completion, per event
    """
    from app.models.learning_path import LearningPath, LearningPathItem, PathItemType
    from app.models.project import Submission, SubmissionStatus

    if unit_type != "user":
        return {variant: {"n": 0} for variant in variant_units}

    # Derivable paths: required items exist and are all projects
    items_q = select(
        LearningPathItem.path_id, LearningPathItem.item_type, LearningPathItem.project_id
    ).where(LearningPathItem.required.is_(True))
    if experiment is not None and experiment.scope_org_id:
        items_q = items_q.join(
            LearningPath, LearningPath.id == LearningPathItem.path_id
        ).where(LearningPath.org_id == experiment.scope_org_id)
    path_projects: dict[str, set[str]] = {}
    underivable: set[str] = set()
    for path_id, item_type, project_id in (await db.execute(items_q)).all():
        if item_type == PathItemType.PROJECT and project_id:
            path_projects.setdefault(path_id, set()).add(project_id)
        else:
            underivable.add(path_id)
    paths = {pid: projs for pid, projs in path_projects.items() if pid not in underivable}
    all_projects = set().union(*paths.values()) if paths else set()

    measure = definition.key
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units or not paths:
            result[variant] = (
                {"n": len(units), "numerator": 0, "denominator": len(units)}
                if measure == "completion_rate"
                else {"n": 0}
            )
            continue
        approved_rows = (
            await db.execute(
                select(
                    Submission.user_id,
                    Submission.project_id,
                    func.min(Submission.updated_at),
                )
                .where(
                    Submission.user_id.in_(units),
                    Submission.project_id.in_(all_projects),
                    Submission.status == SubmissionStatus.APPROVED,
                )
                .group_by(Submission.user_id, Submission.project_id)
            )
        ).all()
        first_rows = (
            await db.execute(
                select(
                    Submission.user_id,
                    Submission.project_id,
                    func.min(Submission.created_at),
                )
                .where(
                    Submission.user_id.in_(units),
                    Submission.project_id.in_(all_projects),
                )
                .group_by(Submission.user_id, Submission.project_id)
            )
        ).all()
        approved_at = {(u, pr): ts for u, pr, ts in approved_rows}
        first_at = {(u, pr): ts for u, pr, ts in first_rows}
        completed_units: set[str] = set()
        durations: list[float] = []
        for user_id in units:
            for _path_id, projects in paths.items():
                times = [approved_at.get((user_id, pr)) for pr in projects]
                if any(t is None for t in times):
                    continue
                completion = max(times)
                if not window_start <= completion < window_end:
                    continue
                completed_units.add(user_id)
                starts = [
                    first_at[(user_id, pr)] for pr in projects if (user_id, pr) in first_at
                ]
                if starts:
                    durations.append((completion - min(starts)).total_seconds() / 3600.0)
        if measure == "completion_rate":
            result[variant] = {
                "n": len(units),
                "numerator": len(completed_units),
                "denominator": len(units),
            }
        else:  # time_to_completion_hours
            durations, winsorized = winsorize(durations, definition.winsorize_pct)
            result[variant] = {
                "n": len(durations),
                "sum_value": sum(durations),
                "sum_sq": sum(d * d for d in durations),
                "_winsorized": winsorized,
            }
            # §4.14: per-event sketch ONLY when the definition asks for
            # quantiles — no silent write amplification
            if definition.spec.get("quantiles"):
                result[variant]["value_histogram"] = value_histogram(durations)
    return result


@register_source("evaluations")
async def _source_evaluations(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Practical assessment pass over user units: SubmissionReview verdicts
    written in-window (AI and instructor alike — the pipeline's own APPROVED
    is the pass semantic, ADR-006/008), per-review binary."""
    from app.models.project import ReviewStatus, Submission, SubmissionReview

    if unit_type != "user":
        return {variant: {"n": 0} for variant in variant_units}
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units:
            result[variant] = {"n": 0}
            continue
        if variance_reduction is not None:
            # Binary CUPED (round 144, same contract as the projects source,
            # round 142): per-UNIT 0/1 — 1 when any of the unit's reviews in
            # the window is APPROVED (ITT; unit-of-analysis change vs
            # per-review mode). _unit_values feeds the covariate assembler.
            rows = (
                await db.execute(
                    select(Submission.user_id, SubmissionReview.status)
                    .join(Submission, Submission.id == SubmissionReview.submission_id)
                    .where(
                        Submission.user_id.in_(units),
                        SubmissionReview.created_at >= window_start,
                        SubmissionReview.created_at < window_end,
                    )
                )
            ).all()
            y: dict[str, float] = dict.fromkeys(units, 0.0)
            for user_id, status in rows:
                if status == ReviewStatus.APPROVED:
                    y[user_id] = 1.0
            passed_units = sum(1 for u in units if y[u] > 0)
            result[variant] = {
                "n": len(units),
                "numerator": passed_units,
                "denominator": len(units),
                "_aggregation": "per_unit",
                "_unit_values": y,
            }
            continue
        rows = (
            await db.execute(
                select(SubmissionReview.status)
                .join(Submission, Submission.id == SubmissionReview.submission_id)
                .where(
                    Submission.user_id.in_(units),
                    SubmissionReview.created_at >= window_start,
                    SubmissionReview.created_at < window_end,
                )
            )
        ).all()
        passed = sum(1 for (status,) in rows if status == ReviewStatus.APPROVED)
        result[variant] = {"n": len(rows), "numerator": passed, "denominator": len(rows)}
    return result


@register_source("talent_outcomes")
async def _source_talent_outcomes(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Placement outcomes over user units (ADR-015 Placement records,
    written when an application reaches hired). Binary-at-horizon per unit:
    a unit converts when a non-cancelled placement lands in-window.
    OBSERVATIONAL ONLY — employment decisions are never randomized
    (ADR-017 §3); this metric exists for observational analyses and
    guardrails, and its experiments are refused promotion at decision time."""
    from app.talent.models.application import Placement

    if unit_type != "user":
        return {variant: {"n": 0} for variant in variant_units}
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units:
            result[variant] = {"n": 0}
            continue
        placed = (
            await db.execute(
                select(func.count(func.distinct(Placement.user_id))).where(
                    Placement.user_id.in_(units),
                    Placement.status != "cancelled",
                    Placement.created_at >= window_start,
                    Placement.created_at < window_end,
                )
            )
        ).scalar_one()
        result[variant] = {"n": len(units), "numerator": placed, "denominator": len(units)}
    return result


@register_source("billing")
async def _source_billing(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Commercial metrics over TENANT units only (billing is tenant-keyed;
    org units would double-count a tenant's revenue across its orgs — the
    unit-type guard refuses rather than mis-join, same rule as cost_ledger).

    conversion_rate    binary: tenant's FIRST paid invoice ever lands in-window
    arpu_usd           continuous: paid revenue per tenant in-window (ITT, zero
                       for silent tenants)
    retention_rate     binary-at-horizon: subscribed at window_start and not
                       cancelled before window_end / subscribed at window_start
    gross_margin_pct   continuous: (revenue - eval cost) / revenue per tenant
                       with in-window revenue
    """
    from app.controlplane.models.billing import Invoice, Subscription
    from app.models.evaluation import EvaluationTask
    from app.models.organization import Organization

    if unit_type != "tenant":
        return {variant: {"n": 0} for variant in variant_units}
    measure = definition.key
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units:
            result[variant] = {"n": 0}
            continue
        if measure == "conversion_rate":
            first_paid = (
                await db.execute(
                    select(Invoice.tenant_id, func.min(Invoice.paid_at))
                    .where(
                        Invoice.tenant_id.in_(units),
                        Invoice.status == "paid",
                        Invoice.paid_at.is_not(None),
                    )
                    .group_by(Invoice.tenant_id)
                )
            ).all()
            converted = sum(
                1 for _tenant, ts in first_paid if window_start <= ts < window_end
            )
            result[variant] = {
                "n": len(units), "numerator": converted, "denominator": len(units),
            }
        elif measure == "retention_rate":
            subs = (
                await db.execute(
                    select(Subscription.tenant_id, Subscription.cancelled_at).where(
                        Subscription.tenant_id.in_(units),
                        Subscription.created_at <= window_start,
                    )
                )
            ).all()
            at_risk: dict[str, bool] = {}
            for tenant_id, cancelled_at in subs:
                if cancelled_at is not None and cancelled_at <= window_start:
                    continue  # already churned before the window
                retained = cancelled_at is None or cancelled_at >= window_end
                # any still-retained subscription keeps the tenant retained
                at_risk[tenant_id] = at_risk.get(tenant_id, False) or retained
            result[variant] = {
                "n": len(at_risk),
                "numerator": sum(1 for kept in at_risk.values() if kept),
                "denominator": len(at_risk),
            }
        elif measure in ("arpu_usd", "gross_margin_pct"):
            paid_rows = (
                await db.execute(
                    select(Invoice.tenant_id, func.sum(Invoice.total_minor))
                    .where(
                        Invoice.tenant_id.in_(units),
                        Invoice.status == "paid",
                        Invoice.paid_at >= window_start,
                        Invoice.paid_at < window_end,
                    )
                    .group_by(Invoice.tenant_id)
                )
            ).all()
            revenue = {t: float(total or 0) / 100.0 for t, total in paid_rows}
            if measure == "arpu_usd":
                values = [revenue.get(t, 0.0) for t in units]
            else:  # gross_margin_pct — only tenants with in-window revenue
                cost_rows = (
                    await db.execute(
                        select(Organization.tenant_id, func.sum(EvaluationTask.cost_usd))
                        .join(Organization, Organization.id == EvaluationTask.org_id)
                        .where(
                            Organization.tenant_id.in_(list(revenue)),
                            EvaluationTask.cost_usd.is_not(None),
                            EvaluationTask.created_at >= window_start,
                            EvaluationTask.created_at < window_end,
                        )
                        .group_by(Organization.tenant_id)
                    )
                ).all() if revenue else []
                cost = {t: float(c or 0) for t, c in cost_rows}
                values = [
                    (rev - cost.get(t, 0.0)) / rev * 100.0
                    for t, rev in revenue.items()
                    if rev > 0
                ]
            values, winsorized = winsorize(values, definition.winsorize_pct)
            result[variant] = {
                "n": len(values),
                "sum_value": sum(values),
                "sum_sq": sum(v * v for v in values),
                "_winsorized": winsorized,
            }
        else:
            result[variant] = {"n": 0}
    return result



@register_source("capabilities")
async def _source_capabilities(
    db: AsyncSession,
    *,
    experiment: Experiment,
    definition: MetricDefinition,
    variant_units: dict[str, list[str]],
    window_start: datetime,
    window_end: datetime,
    unit_type: str = "",
    variance_reduction=None,
) -> SourceResult:
    """Capability gain over user units (ADR-015 score snapshots).

    Per unit: mean over capabilities of (latest in-window composite score −
    latest pre-window baseline), counting only capabilities that have BOTH a
    baseline and an in-window snapshot — a first-ever score is enrollment,
    not gain. Units with no measurable pair contribute nothing (n counts
    units with a gain value)."""
    from app.talent.models.scoring import CapabilityScoreSnapshot as Snap

    if unit_type != "user":
        return {variant: {"n": 0} for variant in variant_units}
    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units:
            result[variant] = {"n": 0}
            continue
        pre_rows = (
            await db.execute(
                select(Snap.user_id, Snap.capability_id, Snap.score, Snap.computed_at)
                .where(Snap.user_id.in_(units), Snap.computed_at < window_start)
                .order_by(Snap.computed_at.desc())
            )
        ).all()
        cur_rows = (
            await db.execute(
                select(Snap.user_id, Snap.capability_id, Snap.score, Snap.computed_at)
                .where(
                    Snap.user_id.in_(units),
                    Snap.computed_at >= window_start,
                    Snap.computed_at < window_end,
                )
                .order_by(Snap.computed_at.desc())
            )
        ).all()
        baseline: dict[tuple[str, str], float] = {}
        for user_id, cap_id, score, _ts in pre_rows:  # desc — first seen wins
            baseline.setdefault((user_id, cap_id), float(score))
        latest: dict[tuple[str, str], float] = {}
        for user_id, cap_id, score, _ts in cur_rows:
            latest.setdefault((user_id, cap_id), float(score))
        values: list[float] = []
        for user_id in units:
            gains = [
                cur - baseline[key]
                for key, cur in latest.items()
                if key[0] == user_id and key in baseline
            ]
            if gains:
                values.append(sum(gains) / len(gains))
        values, winsorized = winsorize(values, definition.winsorize_pct)
        result[variant] = {
            "n": len(values),
            "sum_value": sum(values),
            "sum_sq": sum(v * v for v in values),
            "_winsorized": winsorized,
        }
    return result


SEED_METRIC_DEFINITIONS: list[dict] = [
    # Internal (always computable)
    {"key": "exposure_rate", "title": "Exposure rate", "kind": "rate", "domain": "operational",
     "source_kind": "service", "spec": {"source": "exposures"}},
    # Production (wired via workflow_runs)
    {"key": "run_success_rate", "title": "Workflow run success rate", "kind": "binary",
     "domain": "workflow", "source_kind": "service",
     "spec": {"source": "workflow_runs", "measure": "success_rate"}},
    {"key": "run_latency_ms", "title": "Workflow run latency (ms)", "kind": "continuous",
     "domain": "workflow", "source_kind": "service",
     "spec": {"source": "workflow_runs", "measure": "latency_ms"},
     "direction": "decrease_good", "winsorize_pct": 99.9},
    # Learning — path progress is DERIVED (no progress table); its
    # aggregation source lands with the exp09 hardening pass
    {"key": "completion_rate", "title": "Path completion", "kind": "binary", "domain": "learning",
     "source_kind": "service", "spec": {"source": "learning_paths"}},
    {"key": "time_to_completion_hours", "title": "Time to completion (h)", "kind": "continuous",
     "domain": "learning", "source_kind": "service", "spec": {"source": "learning_paths"},
     "direction": "decrease_good"},
    # Practical pass needs the review pipeline's semantics — exp09
    {"key": "practical_pass_rate", "title": "Practical assessment pass", "kind": "binary",
     "domain": "assessment", "source_kind": "service", "spec": {"source": "evaluations"}},
    {"key": "project_approval_rate", "title": "Project approval", "kind": "binary",
     "domain": "learning", "source_kind": "service",
     "spec": {"source": "projects", "measure": "approval_rate"}},
    {"key": "revision_count", "title": "Revision count", "kind": "continuous",
     "domain": "learning", "source_kind": "service",
     "spec": {"source": "projects", "measure": "revision_count"},
     "direction": "decrease_good"},
    {"key": "capability_gain", "title": "Capability gain", "kind": "continuous",
     "domain": "learning", "source_kind": "service", "spec": {"source": "capabilities"}},
    {"key": "placement_outcome_rate", "title": "Placement outcome", "kind": "time_to_event",
     "domain": "talent_flow", "source_kind": "service", "spec": {"source": "talent_outcomes"}},
    # Production quality/cost
    {"key": "client_acceptance_rate", "title": "Client acceptance", "kind": "binary",
     "domain": "workflow", "source_kind": "service", "spec": {"source": "client_briefs"}},
    {"key": "internal_cost_usd", "title": "Internal cost (USD)", "kind": "continuous",
     "domain": "operational", "source_kind": "service",
     # #69 family: a cost guardrail guards the window TOTAL
     "spec": {"source": "cost_ledger", "guardrail_aggregate": "sum"},
     "direction": "decrease_good"},
    {"key": "provider_reliability", "title": "Provider reliability", "kind": "rate",
     "domain": "workflow", "source_kind": "service", "spec": {"source": "eco_telemetry"}},
    # Commercial
    {"key": "conversion_rate", "title": "Conversion", "kind": "binary", "domain": "marketplace",
     "source_kind": "service", "spec": {"source": "billing"}},
    {"key": "retention_rate", "title": "Retention", "kind": "time_to_event",
     "domain": "marketplace", "source_kind": "service", "spec": {"source": "billing"}},
    {"key": "arpu_usd", "title": "ARPU (USD)", "kind": "continuous", "domain": "marketplace",
     "source_kind": "service", "spec": {"source": "billing"}},
    {"key": "gross_margin_pct", "title": "Gross margin %", "kind": "continuous",
     "domain": "marketplace", "source_kind": "service", "spec": {"source": "billing"}},
    {"key": "pack_adoption_rate", "title": "Pack adoption", "kind": "rate",
     "domain": "marketplace", "source_kind": "service", "spec": {"source": "registry"}},
    # Guardrail staples
    {"key": "cost_usd", "title": "Cost ceiling (USD)", "kind": "continuous",
     "domain": "operational", "source_kind": "service",
     # #69: a cost CEILING guards the window TOTAL — without this the
     # guardrail silently evaluated the mean per task (the sum branch was
     # unreachable: no seed set it and definition.spec is immutable).
     # Seeds are ON CONFLICT DO NOTHING: pre-existing deployments keep the
     # old spec until the definition row is re-seeded (documented, §18).
     "spec": {"source": "cost_ledger", "guardrail_aggregate": "sum"},
     "direction": "decrease_good"},
    {"key": "run_failure_rate", "title": "Run failure rate", "kind": "rate",
     "domain": "operational", "source_kind": "service",
     "spec": {"source": "workflow_runs", "measure": "failure_rate"},
     "direction": "decrease_good"},
]


class MetricService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── definitions ──────────────────────────────────────────────────

    async def ensure_seed_definitions(self) -> int:
        """Idempotent seed: insert missing keys, never overwrite operator edits."""
        created = 0
        for seed in SEED_METRIC_DEFINITIONS:
            insert = (
                pg_insert(MetricDefinition)
                .values(**seed)
                .on_conflict_do_nothing(index_elements=["key"])
            )
            result = await self.db.execute(insert)
            created += result.rowcount or 0
        return created

    async def create_definition(self, **fields) -> MetricDefinition:
        for name, allowed in (
            ("kind", METRIC_KINDS),
            ("source_kind", METRIC_SOURCE_KINDS),
            ("privacy_class", METRIC_PRIVACY_CLASSES),
            ("direction", METRIC_DIRECTIONS),
        ):
            value = fields.get(name)
            if value is not None and value not in allowed:
                raise AppError(
                    "VALIDATION_ERROR", f"Unknown {name}: {value} (allowed: {sorted(allowed)})", 422
                )
        _validate_quantiles(
            (fields.get("spec") or {}).get("quantiles"), fields.get("kind")
        )
        definition = MetricDefinition(**fields)
        self.db.add(definition)
        try:
            await self.db.flush()
        except Exception as exc:  # IntegrityError on unique key
            raise AppError(
                "EXPERIMENT_KEY_TAKEN", f"Metric key taken: {fields.get('key')}", 409
            ) from exc
        return definition

    async def update_definition(self, key: str, **changes) -> MetricDefinition:
        """Round 101: edit the OPERATIONAL knobs of a definition (title,
        privacy class, direction, winsorize/cap). kind/source stay immutable
        — they are analysis semantics baked into stored snapshots."""
        definition = (
            await self.db.execute(
                select(MetricDefinition).where(MetricDefinition.key == key)
            )
        ).scalar_one_or_none()
        if definition is None:
            raise AppError("EXPERIMENT_NOT_FOUND", "Metric definition not found", 404)
        for name, allowed in (
            ("privacy_class", METRIC_PRIVACY_CLASSES),
            ("direction", METRIC_DIRECTIONS),
        ):
            value = changes.get(name)
            if value is not None and value not in allowed:
                raise AppError(
                    "VALIDATION_ERROR",
                    f"Unknown {name}: {value} (allowed: {sorted(allowed)})",
                    422,
                )
        for field in ("title", "privacy_class", "direction",
                      "winsorize_pct", "cap_value"):
            if changes.get(field) is not None:
                setattr(definition, field, changes[field])
        if changes.get("km") is not None:
            if definition.kind != "time_to_event":
                raise AppError(
                    "VALIDATION_ERROR",
                    f"km requires a time_to_event metric (kind: {definition.kind})",
                    422,
                )
            if (changes["km"]
                    and (definition.spec or {}).get("source") != "talent_outcomes"):
                raise AppError(
                    "VALIDATION_ERROR",
                    "km requires a talent_outcomes-sourced metric (the KM "
                    "event reader is placement-based)",
                    422,
                )
            spec = {k: v for k, v in (definition.spec or {}).items() if k != "km"}
            if changes["km"]:
                spec["km"] = True
            definition.spec = spec
        if changes.get("quantiles") is not None:
            _validate_quantiles(changes["quantiles"], definition.kind)
            definition.spec = {**(definition.spec or {}),
                               "quantiles": [float(v) for v in changes["quantiles"]]}
        if changes.get("clear_quantiles"):
            definition.spec = {
                k: v for k, v in (definition.spec or {}).items() if k != "quantiles"
            }
        if changes.get("clear_winsorize"):
            definition.winsorize_pct = None
        if changes.get("clear_cap"):
            definition.cap_value = None
        await self.db.flush()
        return definition

    async def list_definitions(self, *, domain: str | None = None) -> list[MetricDefinition]:
        q = select(MetricDefinition).order_by(MetricDefinition.key.asc())
        if domain:
            q = q.where(MetricDefinition.domain == domain)
        return list((await self.db.execute(q)).scalars())

    # ── snapshots ────────────────────────────────────────────────────

    async def _variant_units(
        self, experiment_id: str, *, as_of: datetime | None = None,
        exposed_only: bool = False,
    ) -> dict[str, list[str]]:
        """ITT unit sets: grouped by assigned variant, holdouts excluded.

        as_of pins the set to units assigned BEFORE that instant — a
        recompute of yesterday's window must not let today's newly assigned
        (necessarily zero-exposure) units dilute yesterday's denominators.

        exposed_only (§4.7 triggered analysis): restrict to units with at
        least one recorded exposure before as_of — the analysis population
        the spec asked for. Exposure-SRM guards the bias this introduces
        when exposure is treatment-affected."""
        q = select(ExperimentAssignment.variant_key, ExperimentAssignment.unit_id).where(
            ExperimentAssignment.experiment_id == experiment_id,
            ExperimentAssignment.is_holdout.is_(False),
        )
        if as_of is not None:
            q = q.where(ExperimentAssignment.assigned_at < as_of)
        if exposed_only:
            exposure_q = select(ExperimentExposure.assignment_id).where(
                ExperimentExposure.experiment_id == experiment_id
            )
            if as_of is not None:
                exposure_q = exposure_q.where(ExperimentExposure.occurred_at < as_of)
            q = q.where(ExperimentAssignment.id.in_(exposure_q))
        units: dict[str, list[str]] = {}
        for variant_key, unit_id in (await self.db.execute(q)).all():
            units.setdefault(variant_key, []).append(unit_id)
        return units

    async def _experiment_metric_keys(self, exp: Experiment) -> tuple[list[str], str]:
        """(ordered unique metric keys, spec unit_type)."""
        latest = (
            await self.db.execute(
                select(ExperimentVersion).where(
                    ExperimentVersion.experiment_id == exp.id,
                    ExperimentVersion.version == exp.current_version,
                )
            )
        ).scalar_one_or_none()
        if latest is None:
            return [], ""
        try:
            spec = ExperimentSpec.model_validate(latest.spec)
        except Exception:  # noqa: BLE001 — poison-spec: skip, never dead-letter forever
            log.error("exp_snapshot_spec_unparseable", experiment_id=exp.id)
            return [], ""
        keys = [*spec.metrics.primary, *spec.metrics.secondary]
        keys.extend(g.metric_key for g in spec.metrics.guardrails)
        # Preserve order, drop duplicates
        return list(dict.fromkeys(keys)), spec.unit_type

    async def compute_experiment_window(
        self, experiment_id: str, *, window_start: datetime, window_end: datetime
    ) -> int:
        """Compute/UPSERT snapshots for every resolvable metric of the
        experiment over one window. Returns the number of snapshots written."""
        exp = await self.db.get(Experiment, experiment_id)
        if not exp:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        metric_keys, unit_type = await self._experiment_metric_keys(exp)
        if not metric_keys:
            return 0
        definitions = {
            d.key: d
            for d in (
                await self.db.execute(
                    select(MetricDefinition).where(MetricDefinition.key.in_(metric_keys))
                )
            ).scalars()
        }
        # CUPED covariate request comes from the experiment spec (§4.6 v2);
        # sources that support it emit per-unit cov_* sufficient stats
        variance_reduction = None
        latest = (
            await self.db.execute(
                select(ExperimentVersion).where(
                    ExperimentVersion.experiment_id == exp.id,
                    ExperimentVersion.version == exp.current_version,
                )
            )
        ).scalar_one_or_none()
        if latest is not None:
            try:
                variance_reduction = ExperimentSpec.model_validate(
                    latest.spec
                ).variance_reduction
            except Exception:  # noqa: BLE001 — poison spec must not kill snapshots
                variance_reduction = None
        # Window-consistent ITT: only units assigned before the window closed.
        # Triggered analysis (§4.7): the spec may narrow the population to
        # EXPOSED units — recorded in provenance so every snapshot says which
        # denominator it carries.
        exposed_only = False
        if latest is not None:
            try:
                exposed_only = (
                    ExperimentSpec.model_validate(latest.spec).trigger.analysis_population
                    == "exposed"
                )
            except Exception:  # noqa: BLE001 — poison spec handled downstream
                exposed_only = False
        variant_units = await self._variant_units(
            experiment_id, as_of=window_end, exposed_only=exposed_only
        )
        if not variant_units:
            return 0
        # Switchback (§4.5): the whole roster belongs to the DAY's variant —
        # per-window snapshots land under the variant that owned the window,
        # so cross-window aggregation compares variant-days.
        if latest is not None:
            try:
                parsed = ExperimentSpec.model_validate(latest.spec)
            except Exception:  # noqa: BLE001 — poison spec handled downstream
                parsed = None
            if parsed is not None and parsed.design == "switchback":
                from app.experiments.services.assignment import (
                    switchback_variant,
                    version_salt_of,
                )

                versions_first = (
                    await self.db.execute(
                        select(ExperimentVersion.spec_hash)
                        .where(ExperimentVersion.experiment_id == exp.id)
                        .order_by(ExperimentVersion.version.asc())
                        .limit(1)
                    )
                ).scalar_one()
                day_variant = switchback_variant(
                    exp.key, version_salt_of(versions_first), parsed, window_start
                )
                roster = sorted({u for units in variant_units.values() for u in units})
                variant_units = {day_variant: roster}
                # Washout (§4.5): drop the carry-over band at the head of the
                # switch window — sources aggregate [start+washout, end) and
                # provenance records the exclusion
                washout = parsed.switchback.washout_minutes if parsed.switchback else 0
                if washout > 0:
                    effective_start = window_start + timedelta(minutes=washout)
                    if effective_start >= window_end:
                        return 0  # the washout swallows the whole window
                    switchback_washout_applied = washout
                    source_window_start = effective_start
                else:
                    switchback_washout_applied = None
                    source_window_start = window_start
            else:
                switchback_washout_applied = None
                source_window_start = window_start
        else:
            switchback_washout_applied = None
            source_window_start = window_start
        # §4.8 segment breakdown: org rows for user-unit experiments that
        # opted in — capped to the biggest 20 orgs by enrolled units so a
        # long org tail cannot blow up the sweep (accumulation-bomb law)
        segment_units: dict[str, dict[str, list[str]]] = {}
        spec_segments: list[str] = []
        if latest is not None:
            try:
                spec_segments = ExperimentSpec.model_validate(latest.spec).segments
            except Exception:  # noqa: BLE001 — poison spec: segments just skip
                spec_segments = []
        if "org" in spec_segments and unit_type == "user":
            from app.models.organization import OrgMember

            all_units = sorted({u for units in variant_units.values() for u in units})
            rows = (
                await self.db.execute(
                    select(OrgMember.user_id, func.min(OrgMember.org_id))
                    .where(OrgMember.user_id.in_(all_units))
                    .group_by(OrgMember.user_id)
                )
            ).all()
            user_org = dict(rows)
            by_org: dict[str, set[str]] = {}
            for user_id, org_id in user_org.items():
                by_org.setdefault(org_id, set()).add(user_id)
            top_orgs = sorted(by_org, key=lambda o: (-len(by_org[o]), o))[:20]
            for org_id in top_orgs:
                members = by_org[org_id]
                segment_units[f"org:{org_id}"] = {
                    variant: [u for u in units if u in members]
                    for variant, units in variant_units.items()
                }

        written = 0
        for key in metric_keys:
            definition = definitions.get(key)
            if definition is None:
                log.warning("experiment_metric_undefined", experiment_id=experiment_id, key=key)
                continue
            source_name = definition.spec.get("source", "")
            source = SOURCE_REGISTRY.get(source_name)
            if source is None:
                # Definition landed before its integration phase — skip, loudly
                log.info(
                    "experiment_metric_source_unwired",
                    experiment_id=experiment_id,
                    key=key,
                    source=source_name,
                )
                continue
            populations = [("", variant_units)] + [
                (seg, seg_units) for seg, seg_units in segment_units.items()
            ]
            for segment, population in populations:
                stats = await source(
                    self.db,
                    experiment=exp,
                    definition=definition,
                    variant_units=population,
                    window_start=source_window_start,
                    window_end=window_end,
                    unit_type=unit_type,
                    variance_reduction=variance_reduction,
                )
                # §4.6 v3 (round 114): multi-covariate assembly — a variant
                # row carrying per-unit y gets every covariate's sufficient
                # stats from the providers; the FIRST covariate mirrors into
                # cov_* so every pre-exp12 reader keeps working
                if variance_reduction is not None:
                    for _vk, _vals in stats.items():
                        unit_values = _vals.pop("_unit_values", None)
                        if not unit_values:
                            continue
                        cov_map = await assemble_covariates(
                            self.db,
                            variance_reduction=variance_reduction,
                            definitions_by_key=definitions,
                            unit_values=unit_values,
                            window_start=window_start,
                        )
                        _vals["covariates"] = cov_map
                        first = variance_reduction.covariates()[0]
                        mirror = cov_map.get(first)
                        if mirror is not None:
                            _vals["cov_sum"] = mirror["sum"]
                            _vals["cov_sum_sq"] = mirror["sum_sq"]
                            _vals["cov_xy_sum"] = mirror["xy_sum"]
                written += await self._write_snapshots(
                    experiment_id=experiment_id,
                    metric_key=key,
                    segment=segment,
                    stats=stats,
                    definition=definition,
                    source_name=source_name,
                    window_start=window_start,
                    window_end=window_end,
                    switchback_washout_applied=switchback_washout_applied,
                    exposed_only=exposed_only,
                )
        return written

    async def _write_snapshots(
        self,
        *,
        experiment_id: str,
        metric_key: str,
        segment: str,
        stats: dict,
        definition,
        source_name: str,
        window_start,
        window_end,
        switchback_washout_applied,
        exposed_only: bool,
    ) -> int:
        written = 0
        # Provenance records what actually happened — no robustness-knob
        # claims here (a source that applies capping/winsorization must
        # be the one to say so; stamping definition.winsorize_pct made
        # provenance assert an adjustment no source performs yet)
        key = metric_key
        provenance = {
            "query_version": definition.query_version,
            "computed_at": datetime.now(UTC).isoformat(),
            "source": source_name,
        }
        if switchback_washout_applied is not None:
            provenance["washout_minutes"] = switchback_washout_applied
        if exposed_only:
            provenance["analysis_population"] = "exposed"
        for variant_key, values in stats.items():
            values = dict(values)
            # Meta flags from the source (not snapshot columns): a source
            # that actually adjusted its values says so in provenance
            variant_provenance = provenance
            values.pop("_unit_values", None)  # per-unit maps never persist
            if values.pop("_winsorized", False):
                variant_provenance = {
                    **variant_provenance,
                    "winsorize_pct": float(definition.winsorize_pct),
                }
            aggregation = values.pop("_aggregation", None)
            if aggregation is not None:
                variant_provenance = {
                    **variant_provenance,
                    "aggregation": aggregation,
                }
            row = {
                "experiment_id": experiment_id,
                "metric_key": key,
                "segment": segment,
                "variant_key": variant_key,
                "window_start": window_start,
                "window_end": window_end,
                "provenance": variant_provenance,
                **values,
            }
            insert = pg_insert(MetricSnapshot).values(**row)
            update_cols = {
                c: insert.excluded[c]
                for c in (
                    "window_end",
                    "n",
                    "numerator",
                    "denominator",
                    "sum_value",
                    "sum_sq",
                    "cov_sum",
                    "cov_sum_sq",
                    "cov_xy_sum",
                    "covariates",
                    "provenance",
                )
                if c in row
            }
            insert = insert.on_conflict_do_update(
                constraint="uq_experiment_metric_snapshots_window", set_=update_cols
            )
            await self.db.execute(insert)
            written += 1
        return written

    async def list_snapshots(
        self, experiment_id: str, *, metric_key: str | None = None, limit: int = 500
    ) -> list[MetricSnapshot]:
        q = select(MetricSnapshot).where(MetricSnapshot.experiment_id == experiment_id)
        if metric_key:
            q = q.where(MetricSnapshot.metric_key == metric_key)
        # id tiebreak on the timestamp order (§99.8)
        q = q.order_by(
            MetricSnapshot.window_start.desc(),
            MetricSnapshot.metric_key.asc(),
            MetricSnapshot.id.desc(),
        ).limit(limit)
        return list((await self.db.execute(q)).scalars())
