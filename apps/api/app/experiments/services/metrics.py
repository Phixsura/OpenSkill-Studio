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
) -> SourceResult:
    """Exposure rate per variant: numerator = exposure events in window,
    denominator = assigned units (ITT). Fully internal — always available."""
    q = (
        select(ExperimentAssignment.variant_key, func.count())
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
        else:
            completed = sum(1 for status, _s, _f in rows if status == RunStatus.COMPLETED)
            result[variant] = {
                "n": len(rows),
                "numerator": completed,
                "denominator": len(rows),
            }
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
    # Learning (sources wired in exp07 — definitions are the contract)
    {"key": "completion_rate", "title": "Path completion", "kind": "binary", "domain": "learning",
     "source_kind": "service", "spec": {"source": "learning_paths"}},
    {"key": "time_to_completion_hours", "title": "Time to completion (h)", "kind": "continuous",
     "domain": "learning", "source_kind": "service", "spec": {"source": "learning_paths"},
     "direction": "decrease_good"},
    {"key": "practical_pass_rate", "title": "Practical assessment pass", "kind": "binary",
     "domain": "assessment", "source_kind": "service", "spec": {"source": "evaluations"}},
    {"key": "project_approval_rate", "title": "Project approval", "kind": "binary",
     "domain": "learning", "source_kind": "service", "spec": {"source": "projects"}},
    {"key": "revision_count", "title": "Revision count", "kind": "continuous",
     "domain": "learning", "source_kind": "service", "spec": {"source": "projects"},
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

    async def _variant_units(self, experiment_id: str) -> dict[str, list[str]]:
        """ITT unit sets: grouped by assigned variant, holdouts excluded."""
        q = select(ExperimentAssignment.variant_key, ExperimentAssignment.unit_id).where(
            ExperimentAssignment.experiment_id == experiment_id,
            ExperimentAssignment.is_holdout.is_(False),
        )
        units: dict[str, list[str]] = {}
        for variant_key, unit_id in (await self.db.execute(q)).all():
            units.setdefault(variant_key, []).append(unit_id)
        return units

    async def _experiment_metric_keys(self, exp: Experiment) -> list[str]:
        latest = (
            await self.db.execute(
                select(ExperimentVersion).where(
                    ExperimentVersion.experiment_id == exp.id,
                    ExperimentVersion.version == exp.current_version,
                )
            )
        ).scalar_one_or_none()
        if latest is None:
            return []
        spec = ExperimentSpec.model_validate(latest.spec)
        keys = [*spec.metrics.primary, *spec.metrics.secondary]
        keys.extend(g.metric_key for g in spec.metrics.guardrails)
        # Preserve order, drop duplicates
        return list(dict.fromkeys(keys))

    async def compute_experiment_window(
        self, experiment_id: str, *, window_start: datetime, window_end: datetime
    ) -> int:
        """Compute/UPSERT snapshots for every resolvable metric of the
        experiment over one window. Returns the number of snapshots written."""
        exp = await self.db.get(Experiment, experiment_id)
        if not exp:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        metric_keys = await self._experiment_metric_keys(exp)
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
        variant_units = await self._variant_units(experiment_id)
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
            )
            provenance = {
                "query_version": definition.query_version,
                "computed_at": datetime.now(UTC).isoformat(),
                "source": source_name,
            }
            if definition.winsorize_pct is not None:
                provenance["winsorize_pct"] = float(definition.winsorize_pct)
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
