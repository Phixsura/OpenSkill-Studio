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
    ExperimentIdentityLink,
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


# Hot-path spec cache (§18 round 16): resolve() re-read the version rows on
# every call. Specs are IMMUTABLE and the entry is keyed by (experiment_id,
# current_version) — a version bump misses automatically, so there is NO
# staleness window; the TTL only bounds memory for dead experiments.
_SPEC_CACHE_TTL_SECONDS = 300.0
_SPEC_CACHE: dict[str, tuple[float, int, "ExperimentSpec", str]] = {}


def forget_spec(experiment_id: str) -> None:
    _SPEC_CACHE.pop(experiment_id, None)


def forget_missing_key(experiment_key: str) -> None:
    """Called on experiment creation so a new surface experiment takes effect
    immediately in this process."""
    _MISSING_KEY_CACHE.pop(experiment_key, None)


SALT_PREFIX_LEN = 8


# Defect #98: per-user cap on identity-graph edges (Segment-class norm)
IDENTITY_LINK_CAP_PER_USER = 100


def version_salt_of(spec_hash: str) -> str:
    """Version-1 randomization salt = the spec hash's first 8 hex chars —
    ONE definition shared by resolution and window attribution; a silent
    divergence would randomize the two sides differently."""
    return spec_hash[:SALT_PREFIX_LEN]


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
        cached = _SPEC_CACHE.get(exp.id)
        if (
            cached is not None
            and cached[0] > time.monotonic()
            and cached[1] == exp.current_version
        ):
            return cached[2], cached[3]
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
        version_salt = version_salt_of(versions[0].spec_hash)
        try:
            spec = ExperimentSpec.model_validate(latest.spec)
        except Exception as exc:  # noqa: BLE001 — poison spec: typed, not a 500
            # never cache a poison spec — a data repair must take effect at once
            forget_spec(exp.id)
            raise AppError(
                "EXPERIMENT_SPEC_INVALID", "Stored spec failed to parse", 422
            ) from exc
        _SPEC_CACHE[exp.id] = (
            time.monotonic() + _SPEC_CACHE_TTL_SECONDS,
            exp.current_version,
            spec,
            version_salt,
        )
        return spec, version_salt

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
        no logging.

        §4.17: "anonymous" is an ID NAMESPACE, not a spec unit type — a
        linked anon id serves the USER's assignments (one person, one
        experience, whichever id the client still holds); an unlinked one
        resolves as a user-typed unit under its own ULID and its history
        migrates in place when the link lands."""
        anon_pending: str | None = None
        if unit_type == "anonymous":
            unit_type = "user"
            link = await self.db.get(ExperimentIdentityLink, unit_id)
            if link is not None:
                # #73 self-heal: idempotent re-link sweeps any orphan
                # anon-keyed rows a pre-fix race may have stranded
                await self.link_identity(
                    anonymous_id=unit_id, user_id=link.user_id
                )
                unit_id = link.user_id
            else:
                anon_pending = unit_id
        exp = await self._load_or_none(experiment_key)
        if exp is None:
            return None
        spec, _ = await self._spec_and_salt(exp)

        if spec.design == "switchback":
            return await self._resolve_switchback(
                exp, spec, unit_type=unit_type, unit_id=unit_id,
                context=context, anon_pending=anon_pending,
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
        if anon_pending is not None:
            # #73 (round 213): a link may have LANDED between the forward
            # check and our insert — without this re-check the anon-keyed
            # row we just wrote is stranded (future resolves forward to the
            # user, who then draws a FRESH variant: one person, two
            # experiences, plus an orphan ITT row). Re-read the link and
            # migrate immediately; link_identity is idempotent and applies
            # the standard user-row-wins conflict rule.
            late_link = await self.db.get(ExperimentIdentityLink, anon_pending)
            if late_link is not None:
                await self.link_identity(
                    anonymous_id=anon_pending, user_id=late_link.user_id
                )
                row = await self._existing(exp.id, "user", late_link.user_id)
                if row is None:  # pragma: no cover — migration guarantees one
                    raise AppError(
                        "EXPERIMENT_NOT_FOUND", "Assignment write lost", 500
                    )
        return self._to_resolved(exp, spec, row)

    async def link_identity(
        self, *, anonymous_id: str, user_id: str
    ) -> dict:
        """§4.17 (round 210): bind an anonymous id to a user — first link
        wins (rebinding to a DIFFERENT user is 422), re-linking the same
        pair is idempotent. Every assignment the anon id holds migrates IN
        PLACE to the user key (variant/bucket/version/assigned_at intact —
        ITT timing and exposure FKs preserved); where the user already
        holds a row in the same experiment, the user row stays
        authoritative, the anon row is removed, and an
        experiment_identity_conflict event keeps both variants on the
        audit trail."""
        from app.experiments.models.audit import ExperimentEvent

        if not (1 <= len(anonymous_id) <= 26) or ":" in anonymous_id:
            raise AppError(
                "VALIDATION_ERROR",
                "anonymous_id must be 1-26 chars with no ':'",
                422,
            )
        # Defect #98: the link table is GLOBAL — without a per-user cap a
        # hostile authenticated caller writes unbounded rows (storage
        # amplification; every POST also runs migration scans). Re-linking
        # an existing pair stays idempotent even at the cap.
        existing_link = await self.db.get(ExperimentIdentityLink, anonymous_id)
        if existing_link is None:
            n_links = (
                await self.db.execute(
                    select(func.count()).select_from(ExperimentIdentityLink).where(
                        ExperimentIdentityLink.user_id == user_id
                    )
                )
            ).scalar_one()
            if n_links >= IDENTITY_LINK_CAP_PER_USER:
                raise AppError(
                    "EXPERIMENT_IDENTITY_LINK_CAP",
                    f"identity link cap reached ({IDENTITY_LINK_CAP_PER_USER} "
                    "anonymous ids per user)",
                    422,
                )
        insert = (
            pg_insert(ExperimentIdentityLink)
            .values(anonymous_id=anonymous_id, user_id=user_id)
            .on_conflict_do_nothing(index_elements=["anonymous_id"])
        )
        await self.db.execute(insert)
        link = await self.db.get(ExperimentIdentityLink, anonymous_id)
        if link is None:  # pragma: no cover — PK guarantees a row
            raise AppError("EXPERIMENT_NOT_FOUND", "Link write lost", 500)
        if link.user_id != user_id:
            raise AppError(
                "EXPERIMENT_IDENTITY_CONFLICT",
                "This anonymous id is already linked to a different user",
                422,
            )
        anon_rows = (
            await self.db.execute(
                select(ExperimentAssignment).where(
                    ExperimentAssignment.unit_type == "user",
                    ExperimentAssignment.unit_id == anonymous_id,
                )
            )
        ).scalars().all()
        migrated = 0
        conflicts = 0
        from sqlalchemy import delete as _delete
        from sqlalchemy import update as _update
        from sqlalchemy.exc import IntegrityError

        async def _fold_conflict(row, existing_user_row):
            # #74 (round 214): the anon row's EXPOSURES are an append-only
            # audit surface — deleting the row would cascade them away.
            # Re-point them at the surviving user assignment first (the
            # exposure happened to this person; the surviving row is this
            # person).
            # #78 (round 251): a dedup key recorded under BOTH identities
            # would make the re-point violate the per-assignment dedup
            # unique — the colliding anon row is a semantic DUPLICATE of an
            # exposure the survivor already holds, so it folds away; only
            # non-colliding rows re-point.
            await self.db.execute(
                _delete(ExperimentExposure).where(
                    ExperimentExposure.assignment_id == row.id,
                    ExperimentExposure.dedup_key.isnot(None),
                    ExperimentExposure.dedup_key.in_(
                        select(ExperimentExposure.dedup_key).where(
                            ExperimentExposure.assignment_id
                            == existing_user_row.id,
                            ExperimentExposure.dedup_key.isnot(None),
                        )
                    ),
                )
            )
            await self.db.execute(
                _update(ExperimentExposure)
                .where(ExperimentExposure.assignment_id == row.id)
                .values(assignment_id=existing_user_row.id)
            )
            self.db.add(ExperimentEvent(
                experiment_id=row.experiment_id,
                actor_user_id=user_id,
                event_type="experiment_identity_conflict",
                payload={
                    "anonymous_id": anonymous_id,
                    "user_id": user_id,
                    "anon_variant": row.variant_key,
                    "user_variant": existing_user_row.variant_key,
                },
            ))
            await self.db.delete(row)

        for row in anon_rows:
            existing_user_row = await self._existing(
                row.experiment_id, "user", user_id
            )
            if existing_user_row is not None:
                conflicts += 1
                await _fold_conflict(row, existing_user_row)
            else:
                try:
                    async with self.db.begin_nested():
                        row.unit_id = user_id
                        await self.db.flush()
                    migrated += 1
                except IntegrityError:
                    # #79 (round 254, the #78 class generalized): a
                    # concurrent resolve created the user row INSIDE the
                    # check-then-update window — re-read and take the
                    # conflict branch; the user row wins, as always.
                    await self.db.refresh(row)  # rollback expired the attrs
                    late_row = await self._existing(
                        row.experiment_id, "user", user_id
                    )
                    if late_row is None:  # pragma: no cover — the violator
                        raise
                    conflicts += 1
                    await _fold_conflict(row, late_row)
        await self.db.flush()
        return {"anonymous_id": anonymous_id, "user_id": user_id,
                "migrated": migrated, "conflicts": conflicts}

    async def _resolve_switchback(
        self,
        exp: Experiment,
        spec: ExperimentSpec,
        *,
        unit_type: str,
        unit_id: str,
        context: dict | None,
        anon_pending: str | None = None,
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
            if anon_pending is not None:
                # #73's switchback mirror (round 215): the same race window
                # exists around the placeholder insert — re-check the link
                # and migrate immediately so no orphan ITT row survives.
                late_link = await self.db.get(
                    ExperimentIdentityLink, anon_pending
                )
                if late_link is not None:
                    await self.link_identity(
                        anonymous_id=anon_pending, user_id=late_link.user_id
                    )
                    existing = await self._existing(
                        exp.id, "user", late_link.user_id
                    )
                    if existing is None:  # pragma: no cover — migration guarantees one
                        raise AppError(
                            "EXPERIMENT_NOT_FOUND", "Assignment write lost", 500
                        )
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
        # #75 (round 214): the exposure surface speaks the same anonymous
        # namespace as resolve — without this, every pre-login exposure was
        # silently dropped (False, the fail-safe) and triggered analyses
        # undercounted linked users.
        original_anon: str | None = None
        if unit_type == "anonymous":
            original_anon = unit_id
            unit_type = "user"
            link = await self.db.get(ExperimentIdentityLink, unit_id)
            if link is not None:
                unit_id = link.user_id
        exp = await self._load_or_none(experiment_key)
        if exp is None:
            return False
        assignment = await self._existing(exp.id, unit_type, unit_id)
        if assignment is None:
            return False
        if assignment.is_holdout:
            # Defect #94: a holdout unit is never served (resolve() returns
            # None) — an exposure for it is a caller bug. Same fail-safe as
            # exposure-without-assignment: refuse, never crash, no row.
            return False

        def _insert_for(assignment_id: str):
            stmt = pg_insert(ExperimentExposure).values(
                assignment_id=assignment_id,
                experiment_id=exp.id,
                context=context or {},
                dedup_key=dedup_key,
            )
            if dedup_key is not None:
                # Targetless DO NOTHING: absorbs the partial-unique dedup
                # conflict
                stmt = stmt.on_conflict_do_nothing()
            return stmt

        from sqlalchemy.exc import IntegrityError

        try:
            async with self.db.begin_nested():
                await self.db.execute(_insert_for(assignment.id))
            return True
        except IntegrityError:
            # #76 (round 223): the assignment row vanished mid-write — an
            # identity-link CONFLICT fold deleted the anon row between our
            # lookup and the insert. The exposure belongs to the PERSON,
            # not the row: re-normalize once under the current link state
            # and retry against the surviving assignment.
            if original_anon is None:
                return False
            link = await self.db.get(ExperimentIdentityLink, original_anon)
            if link is None:
                return False
            survivor = await self._existing(exp.id, "user", link.user_id)
            if survivor is None or survivor.is_holdout:  # 94: same wall on retry
                return False
            await self.db.execute(_insert_for(survivor.id))
            return True

    # ── diagnostics (§12) ────────────────────────────────────────────

    async def list_assignments(
        self, experiment_id: str, *, limit: int = 5000
    ) -> list[ExperimentAssignment]:
        """Round 133: raw assignment rows for the CSV export — stable
        (assigned_at, id) order so a capped export is a deterministic
        prefix, not an arbitrary sample."""
        q = (
            select(ExperimentAssignment)
            .where(ExperimentAssignment.experiment_id == experiment_id)
            .order_by(
                ExperimentAssignment.assigned_at.asc(),
                ExperimentAssignment.id.asc(),
            )
            .limit(limit)
        )
        return list((await self.db.execute(q)).scalars())

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
        # Round 51 (data-flow health): the newest exposure timestamp — the
        # console's "is data still flowing?" signal for running experiments
        last_exposure_at = (
            await self.db.execute(
                select(func.max(ExperimentExposure.occurred_at)).where(
                    ExperimentExposure.experiment_id == experiment_id
                )
            )
        ).scalar_one_or_none()
        return {
            "funnel": funnel,
            "holdout": assigned["holdout"],
            "last_exposure_at": (
                last_exposure_at.isoformat() if last_exposure_at else None
            ),
        }
