"""Deterministic bucketing & sticky assignment (ADR-017 §6, Part B).

Three independent salts keep the rolls uncorrelated:
- ``layer:``   → which slice of the layer hash space the unit occupies
  (mutual exclusion + percentage ramp),
- ``holdout:`` → whether the unit is withheld entirely (long-term control;
  an independent salt so holdout removal does not skew variant proportions),
- ``variant:`` → the point in the cumulative-weight interval.

The variant salt is derived from version 1's spec_hash and NEVER changes
across versions — re-randomization is forbidden under the immutable-spec rule.

Assignment ≠ exposure: resolve() persists the sticky assignment; integration
points call record_exposure() at the moment the variant takes effect.
"""

import hashlib
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models import (
    Experiment,
    ExperimentAssignment,
    ExperimentExposure,
    ExperimentLayerAllocation,
    ExperimentVersion,
)
from app.experiments.schemas import ExperimentSpec, PopulationSpec

BUCKET_SPACE = 10_000

# Statuses in which an existing assignment keeps serving its variant
# (pause stops NEW entries only; completed/analyzed serve until archived)
_SERVE_EXISTING_STATUSES = frozenset({"running", "paused", "completed", "analyzed"})


def _roll(salt: str, *parts: str) -> int:
    digest = hashlib.sha256(":".join((salt, *parts)).encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % BUCKET_SPACE


def bucket(layer_key: str, unit_type: str, unit_id: str) -> int:
    """Layer-slice bucket — shared by every experiment in the layer."""
    return _roll("layer", layer_key, unit_type, unit_id)


def holdout_roll(experiment_key: str, unit_type: str, unit_id: str) -> int:
    return _roll("holdout", experiment_key, unit_type, unit_id)


def variant_roll(experiment_key: str, version_salt: str, unit_type: str, unit_id: str) -> int:
    return _roll("variant", experiment_key, version_salt, unit_type, unit_id)


def pick_variant(spec: ExperimentSpec, roll: int) -> str:
    """Cumulative weight_bp interval lookup over a roll in [0, 10000)."""
    cumulative = 0
    for variant in spec.variants:
        cumulative += variant.weight_bp
        if roll < cumulative:
            return variant.key
    # weights sum to exactly 10000 by spec validation; unreachable
    return spec.variants[-1].key


def in_ramp(*, bucket_value: int, slice_start: int, slice_end: int, ramp_bp: int) -> bool:
    """Ramp widens eligibility from the low end of the slice — integer math,
    monotonic in ramp_bp (a unit admitted at ramp r stays admitted at r' > r)."""
    width = slice_end - slice_start + 1
    local = bucket_value - slice_start
    return local * BUCKET_SPACE < ramp_bp * width


def evaluate_population(population: PopulationSpec, context: dict) -> bool:
    """Whitelisted-field rule evaluation against the caller-provided context.

    All inclusion rules must pass; any matching exclusion rule disqualifies.
    A missing context field fails the rule (fail-closed: no accidental
    enrollment of units we cannot evaluate).
    """

    def matches(rule) -> bool:
        if rule.op == "exists":
            return rule.field in context
        if rule.field not in context:
            return False
        value = context[rule.field]
        if rule.op == "eq":
            return bool(rule.values) and value == rule.values[0]
        if rule.op == "in":
            return value in rule.values
        if rule.op == "not_in":
            return value not in rule.values
        try:
            if rule.op == "gte":
                return float(value) >= float(rule.values[0])
            if rule.op == "lte":
                return float(value) <= float(rule.values[0])
        except (TypeError, ValueError, IndexError):
            return False
        return False

    if any(not matches(rule) for rule in population.rules):
        return False
    return all(not matches(rule) for rule in population.exclusions)


@dataclass(frozen=True)
class ResolvedVariant:
    experiment_key: str
    variant_key: str
    config: dict
    assigned_version: int
    is_holdout: bool


class AssignmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _load(self, experiment_key: str) -> Experiment:
        exp = (
            await self.db.execute(select(Experiment).where(Experiment.key == experiment_key))
        ).scalar_one_or_none()
        if not exp:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        return exp

    async def _spec_and_salt(self, exp: Experiment) -> tuple[ExperimentSpec, str]:
        rows = (
            await self.db.execute(
                select(ExperimentVersion)
                .where(ExperimentVersion.experiment_id == exp.id)
                .order_by(ExperimentVersion.version.asc())
            )
        ).scalars()
        versions = list(rows)
        if not versions:
            raise AppError("EXPERIMENT_SPEC_INVALID", "Experiment has no spec version", 422)
        latest = versions[-1]
        # version 1's hash is the stable randomization salt (§6)
        version_salt = versions[0].spec_hash[:8]
        return ExperimentSpec.model_validate(latest.spec), version_salt

    async def _existing(
        self, experiment_id: str, unit_type: str, unit_id: str
    ) -> ExperimentAssignment | None:
        return (
            await self.db.execute(
                select(ExperimentAssignment).where(
                    ExperimentAssignment.experiment_id == experiment_id,
                    ExperimentAssignment.unit_type == unit_type,
                    ExperimentAssignment.unit_id == unit_id,
                )
            )
        ).scalar_one_or_none()

    def _to_resolved(
        self, exp: Experiment, spec: ExperimentSpec, row: ExperimentAssignment
    ) -> ResolvedVariant | None:
        if row.is_holdout:
            return None
        config = next((v.config for v in spec.variants if v.key == row.variant_key), {})
        return ResolvedVariant(
            experiment_key=exp.key,
            variant_key=row.variant_key,
            config=config,
            assigned_version=row.assigned_version,
            is_holdout=False,
        )

    async def compute(
        self, *, experiment_key: str, unit_type: str, unit_id: str, context: dict | None = None
    ) -> dict:
        """Dry-run the full resolution pipeline WITHOUT writing (§12 preview)."""
        context = context or {}
        exp = await self._load(experiment_key)
        spec, version_salt = await self._spec_and_salt(exp)
        result: dict = {
            "experiment_key": exp.key,
            "status": exp.status,
            "unit_type": unit_type,
            "unit_id": unit_id,
        }
        if unit_type != spec.unit_type:
            result["eligible"] = False
            result["reason"] = f"unit_type mismatch (spec: {spec.unit_type})"
            return result
        if exp.scope_org_id and context.get("org_id") != exp.scope_org_id:
            result["eligible"] = False
            result["reason"] = "unit outside experiment org scope"
            return result
        if not evaluate_population(spec.population, context):
            result["eligible"] = False
            result["reason"] = "population rules"
            return result
        allocation = (
            await self.db.execute(
                select(ExperimentLayerAllocation).where(
                    ExperimentLayerAllocation.experiment_id == exp.id
                )
            )
        ).scalar_one_or_none()
        if not allocation:
            result["eligible"] = False
            result["reason"] = "no layer slice allocation"
            return result
        b = bucket(exp.layer_key, unit_type, unit_id)
        result["bucket"] = b
        if not (allocation.slice_start <= b <= allocation.slice_end):
            result["eligible"] = False
            result["reason"] = "outside layer slice"
            return result
        if not in_ramp(
            bucket_value=b,
            slice_start=allocation.slice_start,
            slice_end=allocation.slice_end,
            ramp_bp=exp.ramp_bp,
        ):
            result["eligible"] = False
            result["reason"] = f"outside ramp ({exp.ramp_bp}bp)"
            return result
        if holdout_roll(exp.key, unit_type, unit_id) < exp.holdout_bp:
            result["eligible"] = True
            result["is_holdout"] = True
            result["variant_key"] = None
            return result
        roll = variant_roll(exp.key, version_salt, unit_type, unit_id)
        result["eligible"] = True
        result["is_holdout"] = False
        result["variant_key"] = pick_variant(spec, roll)
        result["assigned_version"] = exp.current_version
        return result

    async def resolve(
        self, *, experiment_key: str, unit_type: str, unit_id: str, context: dict | None = None
    ) -> ResolvedVariant | None:
        """Sticky, race-safe resolution (ADR-017 §6 steps 1–7)."""
        exp = await self._load(experiment_key)
        spec, _ = await self._spec_and_salt(exp)

        # Sticky first: an existing assignment keeps serving through
        # pause/completion (pause stops NEW entries only)
        existing = await self._existing(exp.id, unit_type, unit_id)
        if existing is not None:
            if exp.status in _SERVE_EXISTING_STATUSES:
                return self._to_resolved(exp, spec, existing)
            return None
        if exp.status != "running":
            return None

        computed = await self.compute(
            experiment_key=experiment_key, unit_type=unit_type, unit_id=unit_id, context=context
        )
        if not computed.get("eligible"):
            return None

        insert = (
            pg_insert(ExperimentAssignment)
            .values(
                experiment_id=exp.id,
                unit_type=unit_type,
                unit_id=unit_id,
                variant_key=computed["variant_key"] or "__holdout__",
                assigned_version=exp.current_version,
                bucket=computed["bucket"],
                is_holdout=computed.get("is_holdout", False),
            )
            .on_conflict_do_nothing(constraint="uq_experiment_assignments_unit")
        )
        await self.db.execute(insert)
        # Re-read as truth — a concurrent resolver may have won the insert
        row = await self._existing(exp.id, unit_type, unit_id)
        if row is None:  # pragma: no cover — unique constraint guarantees a row
            raise AppError("EXPERIMENT_NOT_FOUND", "Assignment write lost", 500)
        return self._to_resolved(exp, spec, row)

    async def record_exposure(
        self,
        *,
        experiment_key: str,
        unit_type: str,
        unit_id: str,
        dedup_key: str | None = None,
        context: dict | None = None,
    ) -> bool:
        """Append one exposure for an assigned unit. Returns False when the
        unit has no assignment (exposure without assignment is a caller bug —
        fail-safe, never crash the product path). Idempotent per dedup_key."""
        exp = await self._load(experiment_key)
        assignment = await self._existing(exp.id, unit_type, unit_id)
        if assignment is None:
            return False
        insert = pg_insert(ExperimentExposure).values(
            assignment_id=assignment.id,
            experiment_id=exp.id,
            context=context or {},
            dedup_key=dedup_key,
        )
        if dedup_key is not None:
            # Targetless DO NOTHING: absorbs the partial-unique dedup conflict
            insert = insert.on_conflict_do_nothing()
        await self.db.execute(insert)
        return True

    # ── diagnostics (§12) ────────────────────────────────────────────

    async def assignment_stats(self, experiment_id: str) -> dict:
        counts_q = (
            select(
                ExperimentAssignment.variant_key,
                ExperimentAssignment.is_holdout,
                func.count(),
            )
            .where(ExperimentAssignment.experiment_id == experiment_id)
            .group_by(ExperimentAssignment.variant_key, ExperimentAssignment.is_holdout)
        )
        rows = (await self.db.execute(counts_q)).all()
        variants: dict[str, int] = {}
        holdout = 0
        for variant_key, is_holdout, count in rows:
            if is_holdout:
                holdout += count
            else:
                variants[variant_key] = count
        return {"variants": variants, "holdout": holdout, "total": sum(variants.values()) + holdout}

    async def exposure_stats(self, experiment_id: str) -> dict:
        """Assignment→exposure funnel per variant (exposure-SRM raw material)."""
        assigned = await self.assignment_stats(experiment_id)
        exposed_q = (
            select(ExperimentAssignment.variant_key, func.count(func.distinct(ExperimentExposure.assignment_id)))
            .join(
                ExperimentAssignment,
                ExperimentAssignment.id == ExperimentExposure.assignment_id,
            )
            .where(ExperimentExposure.experiment_id == experiment_id)
            .group_by(ExperimentAssignment.variant_key)
        )
        exposed = dict((await self.db.execute(exposed_q)).all())
        funnel = {
            variant: {"assigned": count, "exposed_units": exposed.get(variant, 0)}
            for variant, count in assigned["variants"].items()
        }
        return {"funnel": funnel, "holdout": assigned["holdout"]}
