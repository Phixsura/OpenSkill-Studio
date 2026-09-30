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

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

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
) -> SourceResult:
    """Exposure rate per variant: numerator = DISTINCT exposed units in the
    window (a unit hitting the surface five times is one exposed unit — a raw
    event count pushes the rate past 1.0 and false-fires lte guardrails),
    denominator = assigned units (ITT). Fully internal — always available."""
    q = (
        select(
            ExperimentAssignment.variant_key,
            func.count(func.distinct(ExperimentExposure.assignment_id)),
        )
        .join(ExperimentExposure, ExperimentExposure.assignment_id == ExperimentAssignment.id)
        .where(
            ExperimentExposure.experiment_id == experiment.id,
            ExperimentExposure.occurred_at >= window_start,
            ExperimentExposure.occurred_at < window_end,
            ExperimentAssignment.is_holdout.is_(False),
        )
        .group_by(ExperimentAssignment.variant_key)
    )
    counts = dict((await db.execute(q)).all())
    return {
        variant: {
            "n": len(units),
            "numerator": counts.get(variant, 0),
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
            durations = [
                (finished - started).total_seconds() * 1000.0
                for status, started, finished in rows
                if started is not None and finished is not None
            ]
            cap = float(definition.cap_value) if definition.cap_value is not None else None
            if cap is not None:
                durations = [min(d, cap) for d in durations]
            result[variant] = {
                "n": len(durations),
                "sum_value": sum(durations),
                "sum_sq": sum(d * d for d in durations),
            }
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
            revisions = [max(0, version - 1) for _status, version in rows]
            result[variant] = {
                "n": len(revisions),
                "sum_value": sum(revisions),
                "sum_sq": sum(r * r for r in revisions),
            }
        else:
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
) -> SourceResult:
    """Internal cost (USD) from metered evaluation spend, per org/tenant
    units. Money stays Decimal→float at the aggregate boundary only."""
    from app.models.evaluation import EvaluationTask

    result: SourceResult = {}
    for variant, units in variant_units.items():
        if not units or unit_type not in ("organization", "tenant"):
            result[variant] = {"n": 0}
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
        result[variant] = {
            "n": len(costs),
            "sum_value": sum(costs),
            "sum_sq": sum(c * c for c in costs),
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
     "domain": "operational", "source_kind": "service", "spec": {"source": "cost_ledger"},
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
     "domain": "operational", "source_kind": "service", "spec": {"source": "cost_ledger"},
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
        definition = MetricDefinition(**fields)
        self.db.add(definition)
        try:
            await self.db.flush()
        except Exception as exc:  # IntegrityError on unique key
            raise AppError(
                "EXPERIMENT_KEY_TAKEN", f"Metric key taken: {fields.get('key')}", 409
            ) from exc
        return definition

    async def list_definitions(self, *, domain: str | None = None) -> list[MetricDefinition]:
        q = select(MetricDefinition).order_by(MetricDefinition.key.asc())
        if domain:
            q = q.where(MetricDefinition.domain == domain)
        return list((await self.db.execute(q)).scalars())

    # ── snapshots ────────────────────────────────────────────────────

    async def _variant_units(
        self, experiment_id: str, *, as_of: datetime | None = None
    ) -> dict[str, list[str]]:
        """ITT unit sets: grouped by assigned variant, holdouts excluded.

        as_of pins the set to units assigned BEFORE that instant — a
        recompute of yesterday's window must not let today's newly assigned
        (necessarily zero-exposure) units dilute yesterday's denominators."""
        q = select(ExperimentAssignment.variant_key, ExperimentAssignment.unit_id).where(
            ExperimentAssignment.experiment_id == experiment_id,
            ExperimentAssignment.is_holdout.is_(False),
        )
        if as_of is not None:
            q = q.where(ExperimentAssignment.assigned_at < as_of)
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
        spec = ExperimentSpec.model_validate(latest.spec)
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
        # Window-consistent ITT: only units assigned before the window closed
        variant_units = await self._variant_units(experiment_id, as_of=window_end)
        if not variant_units:
            return 0
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
            stats = await source(
                self.db,
                experiment=exp,
                definition=definition,
                variant_units=variant_units,
                window_start=window_start,
                window_end=window_end,
                unit_type=unit_type,
            )
            # Provenance records what actually happened — no robustness-knob
            # claims here (a source that applies capping/winsorization must
            # be the one to say so; stamping definition.winsorize_pct made
            # provenance assert an adjustment no source performs yet)
            provenance = {
                "query_version": definition.query_version,
                "computed_at": datetime.now(UTC).isoformat(),
                "source": source_name,
            }
            for variant_key, values in stats.items():
                row = {
                    "experiment_id": experiment_id,
                    "metric_key": key,
                    "variant_key": variant_key,
                    "window_start": window_start,
                    "window_end": window_end,
                    "provenance": provenance,
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
