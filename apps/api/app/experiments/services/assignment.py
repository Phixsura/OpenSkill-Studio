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
import time
from dataclasses import dataclass
from datetime import UTC, datetime

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

# Hot-path negative cache: surfaces WITHOUT a live experiment (the common
# case for well-known surface keys) must cost ~zero after the first miss —
# without this every registry search / matching run pays experiment lookups
# and logs. Invalidated eagerly by ExperimentService.create (same-process);
# a different process sees a new experiment within the TTL at worst.
_MISSING_KEY_TTL_SECONDS = 60.0
_MISSING_KEY_CACHE: dict[str, float] = {}


def _key_known_missing(experiment_key: str) -> bool:
    expiry = _MISSING_KEY_CACHE.get(experiment_key)
    if expiry is None:
        return False
    if expiry < time.monotonic():
        _MISSING_KEY_CACHE.pop(experiment_key, None)
        return False
    return True


def _remember_missing(experiment_key: str) -> None:
    _MISSING_KEY_CACHE[experiment_key] = time.monotonic() + _MISSING_KEY_TTL_SECONDS


def forget_missing_key(experiment_key: str) -> None:
    """Called on experiment creation so a new surface experiment takes effect
    immediately in this process."""
    _MISSING_KEY_CACHE.pop(experiment_key, None)


def _roll(salt: str, *parts: str) -> int:
    digest = hashlib.sha256(":".join((salt, *parts)).encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % BUCKET_SPACE


def bucket(layer_key: str, unit_type: str, unit_id: str) -> int:
    """Layer-slice bucket — shared by every experiment in the layer."""
    return _roll("layer", layer_key, unit_type, unit_id)


def holdout_roll(experiment_key: str, unit_type: str, unit_id: str) -> int:
    return _roll("holdout", experiment_key, unit_type, unit_id)


def holdout_group_roll(group_key: str, unit_type: str, unit_id: str) -> int:
    """Global holdout-group membership roll (§4.12) — its own salt so group
    membership is uncorrelated with any experiment's layer/holdout/variant."""
    return _roll("holdout-group", group_key, unit_type, unit_id)


def variant_roll(experiment_key: str, version_salt: str, unit_type: str, unit_id: str) -> int:
    return _roll("variant", experiment_key, version_salt, unit_type, unit_id)


def aa_probe(layer_key: str, *, n: int = 2000, unit_type: str = "user") -> dict:
    """A/A hash-health probe (§4.13 v2): bucket n synthetic units into the
    layer's hash space and chi-square the decile occupancy against uniform.
    Deterministic (synthetic ids), pure, zero-I/O — a deploy-time self-check
    that the bucketing hash still spreads. p < 0.001 means the hash layout
    changed (which would re-randomize every live experiment) or the digest
    is broken; both are stop-the-line."""
    from app.experiments.services.analysis import chi2_sf

    n = max(100, min(int(n), 50_000))
    deciles = [0] * 10
    for i in range(n):
        deciles[bucket(layer_key, unit_type, f"aa-probe-{i}") * 10 // BUCKET_SPACE] += 1
    expected = n / 10.0
    chi2 = sum((d - expected) ** 2 / expected for d in deciles)
    p_value = chi2_sf(chi2, 9)
    return {
        "layer_key": layer_key,
        "n": n,
        "deciles": deciles,
        "chi2": round(chi2, 3),
        "p": p_value,
        "healthy": p_value >= 0.001,
    }


SWITCHBACK_PLACEHOLDER = "__switchback__"


def switchback_variant(
    experiment_key: str, version_salt: str, spec: ExperimentSpec, at
) -> str:
    """Switchback design (§4.5 v2): the randomization unit is the TIME
    WINDOW (spec.switchback.window_minutes, epoch-aligned) — every eligible
    unit sees the same variant inside a window, and windows are randomized
    by the same immutable version-1 salt (deterministic schedule, never
    re-randomized). Weight_bp governs each variant's share of windows."""
    window_minutes = spec.switchback.window_minutes if spec.switchback else 1440
    bucket_index = int(at.timestamp() // 60 // window_minutes)
    roll = _roll(
        "variant", experiment_key, version_salt, "switchback", str(bucket_index)
    )
    return pick_variant(spec, roll)


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
        exp = await self._load_or_none(experiment_key)
        if not exp:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        return exp

    async def _load_or_none(self, experiment_key: str) -> Experiment | None:
        """Hot-path load: a surface with no experiment is the COMMON case —
        negative-cached so product paths pay ~nothing (§7 hooks). Keys are
        unique among LIVE experiments only (terminal experiments release the
        key), so resolution binds to the single non-terminal one."""
        if _key_known_missing(experiment_key):
            return None
        from app.experiments.security import TERMINAL_STATUSES

        exp = (
            await self.db.execute(
                select(Experiment).where(
                    Experiment.key == experiment_key,
                    Experiment.status.not_in(TERMINAL_STATUSES),
                )
            )
        ).scalar_one_or_none()
        if exp is None:
            _remember_missing(experiment_key)
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
        try:
            return ExperimentSpec.model_validate(latest.spec), version_salt
        except Exception as exc:  # noqa: BLE001 — poison spec: typed, not a 500
            raise AppError(
                "EXPERIMENT_SPEC_INVALID", "Stored spec failed to parse", 422
            ) from exc

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
        self,
        *,
        unit_type: str,
        unit_id: str,
        experiment: Experiment | None = None,
        experiment_key: str | None = None,
        context: dict | None = None,
    ) -> dict:
        """Dry-run the full resolution pipeline WITHOUT writing (§12 preview).

        Prefer passing the Experiment ROW: keys are unique among live
        experiments only, so key-based lookup on a terminal experiment either
        404s or — worse — binds to a NEWER experiment reusing the key."""
        context = context or {}
        exp = experiment if experiment is not None else await self._load(experiment_key)
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
        # Global holdout groups (§4.12): members are withheld from NEW
        # enrollment across the whole domain (before any per-experiment roll)
        from app.experiments.services.holdouts import active_holdout_groups

        for group_key, group_bp, group_org, _ends in await active_holdout_groups(
            self.db, exp.domain
        ):
            if group_org is not None and group_org != exp.scope_org_id:
                continue
            if holdout_group_roll(group_key, unit_type, unit_id) < group_bp:
                result["eligible"] = False
                result["reason"] = "global holdout group"
                result["holdout_group"] = group_key
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
            # per-unit holdout applies to switchback too: a held-out unit
            # sees the default experience while the cohort switches — the
            # long-term control band is a real knob, never silently ignored
            result["eligible"] = True
            result["is_holdout"] = True
            result["variant_key"] = None
            return result
        if spec.design == "switchback":
            # eligibility settled above; the variant belongs to the WINDOW
            result["eligible"] = True
            result["is_holdout"] = False
            result["switchback"] = True
            result["variant_key"] = switchback_variant(
                exp.key, version_salt, spec, datetime.now(UTC)
            )
            result["assigned_version"] = exp.current_version
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
        """Sticky, race-safe resolution (ADR-017 §6 steps 1–7). An unknown
        key is the normal no-experiment-on-this-surface case → None, cheap,
        no logging."""
        exp = await self._load_or_none(experiment_key)
        if exp is None:
            return None
        spec, _ = await self._spec_and_salt(exp)

        if spec.design == "switchback":
            return await self._resolve_switchback(
                exp, spec, unit_type=unit_type, unit_id=unit_id, context=context
            )

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
            experiment=exp, unit_type=unit_type, unit_id=unit_id, context=context
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

    async def _resolve_switchback(
        self,
        exp: Experiment,
        spec: ExperimentSpec,
        *,
        unit_type: str,
        unit_id: str,
        context: dict | None,
    ) -> ResolvedVariant | None:
        """Switchback resolution: no per-unit stickiness (the whole cohort
        switches together, per §4.5) — a placeholder assignment row keeps the
        exposure FK and the ITT roster, and the served variant is the DAY's.
        Enrollment of NEW units still stops outside running."""
        _, version_salt = await self._spec_and_salt(exp)
        existing = await self._existing(exp.id, unit_type, unit_id)
        if existing is None:
            if exp.status != "running":
                return None
            computed = await self.compute(
                experiment=exp, unit_type=unit_type, unit_id=unit_id, context=context
            )
            if not computed.get("eligible"):
                return None
            is_holdout = bool(computed.get("is_holdout"))
            insert = (
                pg_insert(ExperimentAssignment)
                .values(
                    experiment_id=exp.id,
                    unit_type=unit_type,
                    unit_id=unit_id,
                    variant_key="__holdout__" if is_holdout else SWITCHBACK_PLACEHOLDER,
                    assigned_version=exp.current_version,
                    bucket=computed["bucket"],
                    is_holdout=is_holdout,
                )
                .on_conflict_do_nothing(constraint="uq_experiment_assignments_unit")
            )
            await self.db.execute(insert)
            existing = await self._existing(exp.id, unit_type, unit_id)
            if existing is None:  # pragma: no cover — unique constraint guarantees a row
                raise AppError("EXPERIMENT_NOT_FOUND", "Assignment write lost", 500)
        elif exp.status not in _SERVE_EXISTING_STATUSES:
            return None
        if existing.is_holdout:
            return None  # held-out units see the default experience, sticky
        variant_key = switchback_variant(exp.key, version_salt, spec, datetime.now(UTC))
        config = next((v.config for v in spec.variants if v.key == variant_key), {})
        return ResolvedVariant(
            experiment_key=exp.key,
            variant_key=variant_key,
            config=config,
            assigned_version=existing.assigned_version,
            is_holdout=False,
        )

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
        exp = await self._load_or_none(experiment_key)
        if exp is None:
            return False
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
