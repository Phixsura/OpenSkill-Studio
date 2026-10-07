"""Assignment/exposure DB tests (ADR-017 exp02).

Sticky resolution, ramp/holdout/population gating, pause semantics, exposure
funnel + dedup, and the concurrent double-resolve race (committed data, two
sessions — the ON CONFLICT re-read must make both callers agree).

Runs against the dev Postgres (exp02 applied); rollback-per-test except the
race test, which commits and cleans up after itself.
"""

import asyncio

import pytest
from sqlalchemy import delete, select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.exceptions import AppError
from app.experiments.models import (
    Experiment,
    ExperimentAssignment,
    ExperimentLayer,
    ExperimentLayerAllocation,
)
from app.experiments.security import ETHICS_CHECKLIST_KEY, LAUNCH_CHECKLIST_KEYS
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.layers import LayerService
from app.models.user import User, UserRole, UserStatus

_CHECKLIST = {key: True for key in (*LAUNCH_CHECKLIST_KEYS, ETHICS_CHECKLIST_KEY)}

@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def _spec(**overrides) -> dict:
    base = {
        "hypothesis": "treatment improves the primary metric safely",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "Control", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "Treatment", "weight_bp": 5000,
             "config": {"rubric_template_id": "x"}},
        ],
        "metrics": {
            "primary": ["project_approval_rate"],
            "guardrails": [
                {"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}
            ],
        },
    }
    base.update(overrides)
    return base


async def _mk_admin(db) -> User:
    user = User(
        email=f"exp-admin-{ULID()}@example.com",
        display_name="Exp Admin",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_running(
    db,
    *,
    ramp_bp: int = 10_000,
    holdout_bp: int = 0,
    spec_overrides: dict | None = None,
    slice_start: int = 0,
    slice_end: int = 9999,
) -> tuple[Experiment, User]:
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}",
        title="T",
        domain="learning",
        layer_key=layer.key,
        owner_user_id=admin.id,
        holdout_bp=holdout_bp,
    )
    await svc.create_version(exp.id, spec=_spec(**(spec_overrides or {})), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=slice_start, slice_end=slice_end
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    if ramp_bp:
        await svc.set_ramp(exp.id, ramp_bp=ramp_bp, actor=admin)
    return exp, admin


# ── Sticky resolution ────────────────────────────────────────────────


async def test_resolve_assigns_and_sticks(db):
    exp, _ = await _mk_running(db)
    svc = AssignmentService(db)
    first = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id="u" * 26)
    assert first is not None
    assert first.variant_key in ("control", "treatment")
    assert first.assigned_version == 1
    second = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id="u" * 26)
    assert second == first
    rows = (
        await db.execute(
            select(ExperimentAssignment).where(ExperimentAssignment.experiment_id == exp.id)
        )
    ).scalars()
    assert len(list(rows)) == 1


async def test_variant_split_roughly_matches_weights(db):
    exp, _ = await _mk_running(db)
    svc = AssignmentService(db)
    counts = {"control": 0, "treatment": 0}
    for i in range(400):
        r = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"unit-{i}")
        counts[r.variant_key] += 1
    ratio = counts["control"] / 400
    assert 0.40 < ratio < 0.60, counts


async def test_treatment_config_returned(db):
    exp, _ = await _mk_running(db)
    svc = AssignmentService(db)
    for i in range(50):
        r = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"cfg-{i}")
        if r.variant_key == "treatment":
            assert r.config == {"rubric_template_id": "x"}
            return
    raise AssertionError("no treatment assignment in 50 units")


# ── Gating ───────────────────────────────────────────────────────────


async def test_ramp_zero_admits_nobody(db):
    exp, _ = await _mk_running(db, ramp_bp=0)
    svc = AssignmentService(db)
    for i in range(20):
        assert await svc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=f"r0-{i}"
        ) is None


async def test_outside_slice_not_admitted(db):
    # A 1-wide slice: almost every unit hashes elsewhere
    exp, _ = await _mk_running(db, slice_start=0, slice_end=0)
    svc = AssignmentService(db)
    resolved = [
        await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"s-{i}")
        for i in range(200)
    ]
    assert sum(1 for r in resolved if r is not None) <= 1


async def test_holdout_recorded_and_served_none(db):
    exp, _ = await _mk_running(db, holdout_bp=1000)
    svc = AssignmentService(db)
    outcomes = [
        await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"h-{i}")
        for i in range(300)
    ]
    holdout_rows = list(
        (
            await db.execute(
                select(ExperimentAssignment).where(
                    ExperimentAssignment.experiment_id == exp.id,
                    ExperimentAssignment.is_holdout.is_(True),
                )
            )
        ).scalars()
    )
    assert holdout_rows, "10% holdout produced no holdout assignment in 300 units"
    assert sum(1 for o in outcomes if o is None) == len(holdout_rows)


async def test_unit_type_mismatch_returns_ineligible(db):
    exp, _ = await _mk_running(db)
    result = await AssignmentService(db).compute(
        experiment_key=exp.key, unit_type="cohort", unit_id="c" * 26
    )
    assert result["eligible"] is False
    assert await AssignmentService(db).resolve(
        experiment_key=exp.key, unit_type="cohort", unit_id="c" * 26
    ) is None


async def test_population_rule_fail_closed(db):
    exp, _ = await _mk_running(
        db,
        spec_overrides={
            "population": {"rules": [{"field": "cohort_id", "op": "eq", "values": ["c1"]}]}
        },
    )
    svc = AssignmentService(db)
    assert await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id="p" * 26) is None
    assert (
        await svc.resolve(
            experiment_key=exp.key,
            unit_type="user",
            unit_id="p" * 26,
            context={"cohort_id": "c1"},
        )
        is not None
    )


async def test_paused_serves_existing_but_admits_nobody_new(db):
    exp, admin = await _mk_running(db)
    svc = AssignmentService(db)
    before = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id="a" * 26)
    assert before is not None
    await ExperimentService(db).transition(exp.id, to_status="paused", actor=admin)
    still = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id="a" * 26)
    assert still == before
    assert await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id="b" * 26) is None


async def test_preview_writes_nothing(db):
    exp, _ = await _mk_running(db)
    result = await AssignmentService(db).compute(
        experiment_key=exp.key, unit_type="user", unit_id="dry-run-unit"
    )
    assert result["eligible"] is True
    rows = list(
        (
            await db.execute(
                select(ExperimentAssignment).where(
                    ExperimentAssignment.experiment_id == exp.id
                )
            )
        ).scalars()
    )
    assert rows == []


# ── Exposures ────────────────────────────────────────────────────────


async def test_exposure_funnel_and_dedup(db):
    exp, _ = await _mk_running(db)
    svc = AssignmentService(db)
    r = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id="e" * 26)
    assert r is not None
    assert await svc.record_exposure(
        experiment_key=exp.key, unit_type="user", unit_id="e" * 26, dedup_key="k1"
    )
    # Same dedup key: idempotent under at-least-once callers
    assert await svc.record_exposure(
        experiment_key=exp.key, unit_type="user", unit_id="e" * 26, dedup_key="k1"
    )
    stats = await svc.exposure_stats(exp.id)
    assert stats["funnel"][r.variant_key]["assigned"] == 1
    assert stats["funnel"][r.variant_key]["exposed_units"] == 1
    # wave-29: the exposure CONTEXT persists verbatim (a truthy context was
    # droppable by an or->and mutant with nothing pinning the stored value)
    assert await svc.record_exposure(
        experiment_key=exp.key, unit_type="user", unit_id="e" * 26,
        dedup_key="k2", context={"surface": "dashboard", "variant_seen": True},
    )
    from sqlalchemy import select as _select

    from app.experiments.models import ExperimentExposure as _Exposure
    stored = (
        await db.execute(
            _select(_Exposure).where(
                _Exposure.experiment_id == exp.id,
                _Exposure.dedup_key == "k2",
            )
        )
    ).scalar_one()
    assert stored.context == {"surface": "dashboard", "variant_seen": True}


async def test_exposure_without_assignment_is_failsafe_false(db):
    exp, _ = await _mk_running(db)
    ok = await AssignmentService(db).record_exposure(
        experiment_key=exp.key, unit_type="user", unit_id="never-assigned"
    )
    assert ok is False


# ── The race (committed data, two sessions) ──────────────────────────


async def test_concurrent_resolve_single_row(db):
    """Two sessions resolving the same unit concurrently must both return the
    SAME variant and leave exactly one assignment row (ON CONFLICT + re-read).
    Uses committed fixtures; cleans up after itself."""
    exp, _ = await _mk_running(db)
    exp_key, exp_id = exp.key, exp.id
    await db.commit()

    async def resolve_once():
        async with AsyncSessionLocal() as session:
            svc = AssignmentService(session)
            result = await svc.resolve(
                experiment_key=exp_key, unit_type="user", unit_id="race-unit"
            )
            await session.commit()
            return result

    try:
        results = await asyncio.gather(*[resolve_once() for _ in range(4)])
        keys = {r.variant_key for r in results if r is not None}
        assert len(keys) == 1, results
        async with AsyncSessionLocal() as session:
            rows = list(
                (
                    await session.execute(
                        select(ExperimentAssignment).where(
                            ExperimentAssignment.experiment_id == exp_id
                        )
                    )
                ).scalars()
            )
            assert len(rows) == 1
    finally:
        async with AsyncSessionLocal() as session:
            exp_row = await session.get(Experiment, exp_id)
            layer_key = exp_row.layer_key if exp_row else None
            owner_id = exp_row.owner_user_id if exp_row else None
            await session.execute(
                delete(ExperimentLayerAllocation).where(
                    ExperimentLayerAllocation.experiment_id == exp_id
                )
            )
            await session.execute(delete(Experiment).where(Experiment.id == exp_id))
            if layer_key:
                await session.execute(
                    delete(ExperimentLayer).where(ExperimentLayer.key == layer_key)
                )
            if owner_id:
                await session.execute(delete(User).where(User.id == owner_id))
            await session.commit()


# ── Switchback resolution (v2 batch 11, §4.5) ────────────────────────


async def test_switchback_units_share_the_day_variant(db):
    """All units get the DAY's variant (no per-unit split); the stored row is
    the placeholder (exposure FK + ITT roster), never a served variant."""
    exp, _ = await _mk_running(db, spec_overrides={"design": "switchback", "switchback": {"switch_unit": "platform_day", "window_minutes": 1440}})
    svc = AssignmentService(db)
    resolved = [
        await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"sb-{i}")
        for i in range(10)
    ]
    assert all(r is not None for r in resolved)
    day_variants = {r.variant_key for r in resolved}
    assert len(day_variants) == 1
    assert day_variants < {"control", "treatment"}
    rows = list(
        (
            await db.execute(
                select(ExperimentAssignment).where(
                    ExperimentAssignment.experiment_id == exp.id
                )
            )
        ).scalars()
    )
    assert len(rows) == 10
    assert {r.variant_key for r in rows} == {"__switchback__"}
    # exposure records attach to the placeholder row
    assert await svc.record_exposure(
        experiment_key=exp.key, unit_type="user", unit_id="sb-0"
    )


async def test_switchback_pause_stops_new_entries_only(db):
    exp, admin = await _mk_running(db, spec_overrides={"design": "switchback", "switchback": {"switch_unit": "platform_day", "window_minutes": 1440}})
    svc = AssignmentService(db)
    before = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id="sb-x")
    assert before is not None
    await ExperimentService(db).transition(exp.id, to_status="paused", actor=admin)
    # existing roster member keeps being served the day variant
    still = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id="sb-x")
    assert still is not None
    # a NEW unit is refused
    assert await svc.resolve(
        experiment_key=exp.key, unit_type="user", unit_id="sb-new"
    ) is None


async def test_switchback_honors_per_unit_holdout(db):
    """A held-out unit under switchback sees the DEFAULT experience while
    the cohort switches (the holdout knob is real, never silently ignored);
    ITT rosters exclude it (is_holdout row, sticky)."""
    from app.experiments.services.assignment import holdout_roll

    exp, _ = await _mk_running(
        db, holdout_bp=2000,
        spec_overrides={"design": "switchback",
                        "switchback": {"switch_unit": "platform_day",
                                       "window_minutes": 1440}},
    )
    svc = AssignmentService(db)
    held = nonheld = None
    i = 0
    while held is None or nonheld is None:
        uid = f"sbh{i:023d}"
        if holdout_roll(exp.key, "user", uid) < 2000:
            held = held or uid
        else:
            nonheld = nonheld or uid
        i += 1
    assert await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=held) is None
    # sticky: second resolve still None, and the row is a holdout row
    assert await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=held) is None
    row = (
        await db.execute(
            select(ExperimentAssignment).where(
                ExperimentAssignment.experiment_id == exp.id,
                ExperimentAssignment.unit_id == held,
            )
        )
    ).scalar_one()
    assert row.is_holdout is True
    served = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=nonheld)
    assert served is not None and served.variant_key in ("control", "treatment")


# ── Self-serve resolution surface (v2 batch 27, §7 client-SDK class) ──


async def test_self_serve_resolve_is_sticky_and_self_scoped(db):
    """The facade path the self-serve endpoints call: resolving as a user
    creates the sticky assignment for THAT user only; an unknown key is the
    default experience (None), never an error."""
    from app.experiments import facade

    exp, _ = await _mk_running(db)
    user_id = "u" * 26
    first = await facade.resolve_variant(
        db, experiment_key=exp.key, unit_type="user", unit_id=user_id
    )
    assert first is not None
    second = await facade.resolve_variant(
        db, experiment_key=exp.key, unit_type="user", unit_id=user_id
    )
    assert second == first
    rows = list(
        (
            await db.execute(
                select(ExperimentAssignment).where(
                    ExperimentAssignment.experiment_id == exp.id
                )
            )
        ).scalars()
    )
    assert [r.unit_id for r in rows] == [user_id]
    # unknown surface: default experience, no exception
    assert await facade.resolve_variant(
        db, experiment_key="surface-nothing-here", unit_type="user", unit_id=user_id
    ) is None
    # exposure through the facade for the same unit
    assert await facade.record_exposure(
        db, experiment_key=exp.key, unit_type="user", unit_id=user_id, dedup_key="d1"
    )


# ── Hot-path spec cache (round 16): version-keyed, zero staleness ─────


async def test_spec_cache_hits_without_queries_and_follows_versions(db):
    """Second resolution serves the spec from the process cache (zero DB
    round trips); a version bump misses AUTOMATICALLY because the entry is
    keyed by current_version — no staleness window to reason about."""
    from app.experiments.models import ExperimentVersion
    from app.experiments.services.assignment import forget_spec

    exp, admin = await _mk_running(db)
    svc = AssignmentService(db)
    forget_spec(exp.id)
    spec1, salt1 = await svc._spec_and_salt(exp)  # noqa: SLF001 — fills the cache

    calls = {"n": 0}
    real_execute = db.execute

    async def counting_execute(*args, **kwargs):
        calls["n"] += 1
        return await real_execute(*args, **kwargs)

    db.execute = counting_execute  # type: ignore[method-assign]
    try:
        spec2, salt2 = await svc._spec_and_salt(exp)  # noqa: SLF001
    finally:
        db.execute = real_execute  # type: ignore[method-assign]
    assert calls["n"] == 0
    assert spec2 is spec1 and salt2 == salt1

    # version bump: same experiment row, new current_version → cache miss,
    # fresh spec parsed, SAME v1 salt (immutable randomization)
    import json

    from app.experiments.services.experiments import canonical_spec_hash

    new_spec = json.loads(json.dumps(spec1.model_dump()))
    new_spec["hypothesis"] = "version two reaches resolution immediately"
    db.add(ExperimentVersion(
        experiment_id=exp.id, version=2, spec=new_spec,
        spec_hash=canonical_spec_hash(new_spec), created_by=admin.id,
    ))
    exp.current_version = 2
    await db.flush()
    spec3, salt3 = await svc._spec_and_salt(exp)  # noqa: SLF001
    assert spec3.hypothesis == "version two reaches resolution immediately"
    assert salt3 == salt1  # v1 hash stays the salt forever


# ── Round-21 mutation killers (experiments service) ──────────────────


def test_experiments_error_status_contract_pinned_by_source():
    """The round-20 AST contract, extended to the experiments service."""
    import ast
    from pathlib import Path

    src = (
        Path(__file__).resolve().parents[1]
        / "app" / "experiments" / "services" / "experiments.py"
    )
    found: dict[str, set[int]] = {}
    for node in ast.walk(ast.parse(src.read_text(encoding="utf-8"))):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "AppError"
            and len(node.args) >= 3
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[2], ast.Constant)
        ):
            found.setdefault(node.args[0].value, set()).add(node.args[2].value)
    assert found == {
        "EXPERIMENT_CHECKLIST_INCOMPLETE": {422},
        "EXPERIMENT_DECISION_REQUIRED": {422},
        "EXPERIMENT_INVALID_TRANSITION": {422},
        "EXPERIMENT_KEY_TAKEN": {409},
        "EXPERIMENT_NOT_FOUND": {404},
        "EXPERIMENT_NOTE_CAP": {422},
        "EXPERIMENT_NO_GUARDRAILS": {422},
        "EXPERIMENT_UNKNOWN_METRICS": {422},
        "EXPERIMENT_RAMP_DECREASE": {422},
        "EXPERIMENT_SPEC_INVALID": {422},
        "FORBIDDEN": {403},
        "VALIDATION_ERROR": {422},
    }, found


async def test_spec_size_cap_boundary_exact(db):
    """64000 bytes is LEGAL, 64001 is not (Gt→GtE killer) — padded to the
    exact canonical size programmatically."""
    import json

    from app.experiments.services.experiments import ExperimentService

    svc = ExperimentService(db)
    base = _spec()

    def _sized(padding: int) -> dict:
        import copy

        s2 = copy.deepcopy(base)
        s2["variants"][1]["config"] = {"pad": "h" * padding}
        return s2

    def _raw(spec: dict) -> int:
        return len(json.dumps(spec, separators=(",", ":"), ensure_ascii=False))

    pad = 10
    while _raw(_sized(pad)) < 64_000:
        pad += 64_000 - _raw(_sized(pad))
    exact = _sized(pad - (_raw(_sized(pad)) - 64_000))
    assert _raw(exact) == 64_000
    svc.validate_spec(exact, domain="learning", risk_class="medium")  # legal
    over = _sized(pad - (_raw(_sized(pad)) - 64_000) + 1)
    assert _raw(over) == 64_001
    with pytest.raises(AppError) as e:
        svc.validate_spec(over, domain="learning", risk_class="medium")
    assert e.value.code == "EXPERIMENT_SPEC_INVALID"


async def test_guardrail_exemption_matrix(db):
    """needs_guardrails = NOT (low AND exempt-domain): all three non-exempt
    corners refuse scheduling without guardrails; the exempt corner passes."""
    from ulid import ULID as _ULID

    from app.experiments.services.experiments import ExperimentService
    from app.experiments.services.layers import LayerService as LayerSvc

    async def _to_review(domain: str, risk: str):
        admin = await _mk_admin(db)
        layer = await LayerSvc(db).create(key=f"lyr-{str(_ULID()).lower()}", domain=domain)
        svc = ExperimentService(db)
        exp = await svc.create(
            key=f"exp-{str(_ULID()).lower()}", title="G", domain=domain,
            layer_key=layer.key, owner_user_id=admin.id, risk_class=risk,
        )
        spec = _spec()
        spec["metrics"] = {"primary": ["exposure_rate"], "guardrails": []}
        await svc.create_version(exp.id, spec=spec, actor=admin)
        await LayerSvc(db).allocate(
            layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
        )
        await svc.transition(exp.id, to_status="review", actor=admin)
        return svc, exp, admin

    # low + operational (exempt): schedules without guardrails
    svc, exp, admin = await _to_review("operational", "low")
    await svc.transition(exp.id, to_status="scheduled", actor=admin,
                         checklist=_CHECKLIST)
    assert (await svc.get(exp.id)).status == "scheduled"
    # low + learning (NOT exempt): refused
    svc, exp, admin = await _to_review("learning", "low")
    with pytest.raises(AppError) as e:
        await svc.transition(exp.id, to_status="scheduled", actor=admin,
                             checklist=_CHECKLIST)
    assert e.value.code == "EXPERIMENT_NO_GUARDRAILS"
    # medium + operational (NOT exempt): refused
    svc, exp, admin = await _to_review("operational", "medium")
    with pytest.raises(AppError) as e:
        await svc.transition(exp.id, to_status="scheduled", actor=admin,
                             checklist=_CHECKLIST)
    assert e.value.code == "EXPERIMENT_NO_GUARDRAILS"


async def test_high_risk_schedule_needs_platform_admin_even_delegated(db):
    """The high-risk gate holds against delegated writers: a non-platform
    actor scheduling a high-risk experiment gets FORBIDDEN/403; the platform
    admin passes the same gate."""
    from ulid import ULID as _ULID

    from app.experiments.services.experiments import ExperimentService
    from app.experiments.services.layers import LayerService as LayerSvc

    admin = await _mk_admin(db)
    operator = User(
        email=f"hr-{_ULID()}@example.com", display_name="Op",
        role=UserRole.INSTRUCTOR, status=UserStatus.ACTIVE,
    )
    db.add(operator)
    await db.flush()
    layer = await LayerSvc(db).create(key=f"lyr-{str(_ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(_ULID()).lower()}", title="HR", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id, risk_class="high",
    )
    await svc.create_version(exp.id, spec=_spec(), actor=admin)
    await LayerSvc(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    with pytest.raises(AppError) as e:
        await svc.transition(exp.id, to_status="scheduled", actor=operator,
                             checklist=_CHECKLIST)
    assert e.value.code == "FORBIDDEN"
    assert e.value.status_code == 403
    await svc.transition(exp.id, to_status="scheduled", actor=admin,
                         checklist=_CHECKLIST)
    assert (await svc.get(exp.id)).status == "scheduled"


async def test_ramp_equal_value_is_not_a_decrease(db):
    """`ramp_bp < exp.ramp_bp` killer: setting the SAME value while running
    is legal (idempotent re-apply); one bp less is refused."""
    exp, _ = await _mk_running(db, ramp_bp=5000)
    from app.experiments.services.experiments import ExperimentService

    svc = ExperimentService(db)
    admin = await _mk_admin(db)
    await svc.set_ramp(exp.id, ramp_bp=5000, actor=admin)  # equal: fine
    with pytest.raises(AppError) as e:
        await svc.set_ramp(exp.id, ramp_bp=4999, actor=admin)
    assert e.value.code == "EXPERIMENT_RAMP_DECREASE"


async def test_layer_allocation_boundary_matrix(db):
    """Wave-9 killers: slice_end == total_slices-1 legal, == total_slices
    refused; adjacent slices legal; single-point overlap refused on BOTH
    edges; plus the layers error-status AST contract."""
    import ast
    from pathlib import Path

    from ulid import ULID as _ULID

    from app.experiments.services.experiments import ExperimentService
    from app.experiments.services.layers import LayerService as LayerSvc

    admin = await _mk_admin(db)
    layer = await LayerSvc(db).create(key=f"lyr-{str(_ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)

    async def _exp():
        e = await svc.create(
            key=f"exp-{str(_ULID()).lower()}", title="L", domain="learning",
            layer_key=layer.key, owner_user_id=admin.id,
        )
        return e.id

    a, b, c = await _exp(), await _exp(), await _exp()
    # top boundary: 9999 legal (total_slices 10000), 10000 refused
    await LayerSvc(db).allocate(
        layer_key=layer.key, experiment_id=a, slice_start=5000, slice_end=9999
    )
    with pytest.raises(AppError) as e:
        await LayerSvc(db).allocate(
            layer_key=layer.key, experiment_id=b, slice_start=0, slice_end=10_000
        )
    assert e.value.code == "VALIDATION_ERROR"
    # adjacent is legal...
    await LayerSvc(db).allocate(
        layer_key=layer.key, experiment_id=b, slice_start=0, slice_end=4999
    )
    # ...but sharing a single point on either edge is an overlap
    for start, end in ((4999, 4999), (9999, 9999), (0, 0)):
        with pytest.raises(AppError) as e:
            await LayerSvc(db).allocate(
                layer_key=layer.key, experiment_id=c, slice_start=start, slice_end=end
            )
        assert e.value.code == "LAYER_SLICE_OVERLAP"
        assert e.value.status_code == 409

    src = (
        Path(__file__).resolve().parents[1]
        / "app" / "experiments" / "services" / "layers.py"
    )
    found: dict[str, set[int]] = {}
    for node in ast.walk(ast.parse(src.read_text(encoding="utf-8"))):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "AppError"
            and len(node.args) >= 3
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[2], ast.Constant)
        ):
            found.setdefault(node.args[0].value, set()).add(node.args[2].value)
    assert found == {
        "EXPERIMENT_KEY_TAKEN": {409},
        "EXPERIMENT_NOT_FOUND": {404},
        "LAYER_SLICE_OVERLAP": {409},
        "VALIDATION_ERROR": {422},
    }, found


async def test_facade_db_error_does_not_poison_host_session(db):
    """Defect #41: a mid-flush DB error inside the facade (natural trigger:
    unit_id one char over the varchar(26) column) must roll back to a
    SAVEPOINT — the host session stays healthy and the host's PRIOR
    uncommitted business write survives. Without the savepoint the session
    enters PendingRollback and the HOST's own later commit explodes —
    the experiment breaking the product path it rode along with."""
    from app.experiments import facade

    exp, admin = await _mk_running(db)
    # host business write BEFORE the experiment touchpoint
    host_row = User(
        email=f"host-{ULID()}@example.com", display_name="H",
        role=UserRole.STUDENT, status=UserStatus.ACTIVE,
    )
    db.add(host_row)
    await db.flush()

    # 27 chars > varchar(26) -> StringDataRightTruncation at flush time
    resolved = await facade.resolve_variant(
        db, experiment_key=exp.key, unit_type="user", unit_id="u" * 27
    )
    assert resolved is None  # fail-safe default served
    exposed = await facade.record_exposure(
        db, experiment_key=exp.key, unit_type="user", unit_id="u" * 27
    )
    assert exposed is False

    # the session is NOT poisoned: flush works and the host write is intact
    await db.flush()
    assert await db.get(User, host_row.id) is not None
    # and the surface still works for the next (valid) unit
    ok = await facade.resolve_variant(
        db, experiment_key=exp.key, unit_type="user", unit_id="after-poison"
    )
    assert ok is not None


async def test_exposure_stats_carries_last_exposure_at(db):
    """Round 51: the funnel diagnostics carry the newest exposure timestamp
    (the console's data-flow signal) — None before any exposure, ISO after."""
    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    assert await asvc.resolve(
        experiment_key=exp.key, unit_type="user", unit_id="flow-1"
    ) is not None
    stats = await asvc.exposure_stats(exp.id)
    assert stats["last_exposure_at"] is None
    assert await asvc.record_exposure(
        experiment_key=exp.key, unit_type="user", unit_id="flow-1"
    )
    stats = await asvc.exposure_stats(exp.id)
    assert isinstance(stats["last_exposure_at"], str)


async def test_shared_dedup_key_never_swallows_other_units(db):
    """Defect #58: dedup is PER ASSIGNMENT. Two units recording with the
    SAME natural key (the client's per-day key is the same string for every
    user) must BOTH land; the same unit repeating the key stays one row."""
    from sqlalchemy import func as _func
    from sqlalchemy import select as _select

    from app.experiments.models import ExperimentExposure

    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    for uid in ("dd-user-a", "dd-user-b"):
        assert await asvc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=uid
        ) is not None
        assert await asvc.record_exposure(
            experiment_key=exp.key, unit_type="user", unit_id=uid,
            dedup_key="todo-2026-10-02",
        )
    # repeat for one unit — absorbed, not duplicated
    assert await asvc.record_exposure(
        experiment_key=exp.key, unit_type="user", unit_id="dd-user-a",
        dedup_key="todo-2026-10-02",
    )
    n = (
        await db.execute(
            _select(_func.count()).where(
                ExperimentExposure.experiment_id == exp.id,
                ExperimentExposure.dedup_key == "todo-2026-10-02",
            )
        )
    ).scalar_one()
    assert n == 2  # one per unit — the second unit was previously swallowed


async def test_facade_record_exposure_exception_arm(db, monkeypatch):
    """Round 74 (coverage audit payoff): the facade's record_exposure except
    arm was never exercised — a raising service must yield False with the
    session healthy (the #41 savepoint confines the damage)."""
    from sqlalchemy import text as _text

    from app.experiments import facade
    from app.experiments.services.assignment import AssignmentService as _Svc

    async def _boom(self, **kwargs):
        await self.db.execute(_text("select * from __nope__"))

    monkeypatch.setattr(_Svc, "record_exposure", _boom)
    exp, _ = await _mk_running(db)
    assert await facade.record_exposure(
        db, experiment_key=exp.key, unit_type="user", unit_id="exc-arm"
    ) is False
    await db.flush()  # session not poisoned


async def test_assignment_cold_branches_necropsy(db):
    """Round 76 (necropsy batch): the compute/resolve branches the suites
    never touched — org-scope mismatch, missing layer allocation, unknown-key
    exposure, holdout tally in assignment_stats, and a non-serving
    switchback status."""
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization

    # org-scoped experiment + WRONG org context -> ineligible with reason
    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}",
                           slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(name="scope", slug=f"sc-{str(ULID()).lower()}",
                       tenant_id=tenant.id)
    db.add(org)
    await db.flush()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="learning"
    )
    svc = ExperimentService(db)
    scoped = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="S", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id, scope_org_id=org.id,
    )
    await svc.create_version(scoped.id, spec=_spec(), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=scoped.id, slice_start=0, slice_end=9999
    )
    await svc.transition(scoped.id, to_status="review", actor=admin)
    await svc.transition(scoped.id, to_status="scheduled", actor=admin,
                         checklist=_CHECKLIST)
    await svc.transition(scoped.id, to_status="running", actor=admin)
    await svc.set_ramp(scoped.id, ramp_bp=10_000, actor=admin)
    asvc = AssignmentService(db)
    wrong = await asvc.compute(
        experiment=scoped, unit_type="user", unit_id="necro-1",
        context={"org_id": "x" * 26},
    )
    assert wrong["eligible"] is False
    assert "org scope" in wrong["reason"]

    # experiment WITHOUT a layer allocation -> ineligible with reason
    bare_layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="learning"
    )
    bare = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="B", domain="learning",
        layer_key=bare_layer.key, owner_user_id=admin.id,
    )
    await svc.create_version(bare.id, spec=_spec(), actor=admin)
    unalloc = await asvc.compute(
        experiment=bare, unit_type="user", unit_id="necro-2"
    )
    assert unalloc["eligible"] is False
    assert "allocation" in unalloc["reason"]

    # unknown experiment key on the exposure path -> fail-safe False
    assert await asvc.record_exposure(
        experiment_key="no-such-experiment", unit_type="user", unit_id="necro-3"
    ) is False

    # holdout tally: a per-unit holdout unit lands in the holdout counter
    held_exp, _ = await _mk_running(db, holdout_bp=10_000)
    r = await asvc.resolve(
        experiment_key=held_exp.key, unit_type="user", unit_id="necro-4"
    )
    assert r is None  # held out
    stats = await asvc.assignment_stats(held_exp.id)
    assert stats["holdout"] == 1
    assert stats["variants"] == {}

    # a non-serving status on the switchback path -> None
    sb, sb_admin = await _mk_running(db, spec_overrides={
        "design": "switchback",
        "switchback": {"switch_unit": "platform_day", "window_minutes": 1440},
    })
    await svc.transition(sb.id, to_status="completed", actor=sb_admin)
    await svc.transition(sb.id, to_status="archived", actor=sb_admin)
    assert await asvc.resolve(
        experiment_key=sb.key, unit_type="user", unit_id="necro-5"
    ) is None


async def test_experiments_service_cold_arms_necropsy(db):
    """Round 83: experiments-service arms the unit suites never ran — the
    search body (filters, delegation scope, keyset cursor), list_events,
    uniform 404s, create validations, and the wrong-status guards."""
    admin = await _mk_admin(db)
    svc = ExperimentService(db)

    with pytest.raises(AppError) as exc:
        await svc.get("0" * 26)
    assert exc.value.status_code == 404
    with pytest.raises(AppError):
        await svc.get_versions("0" * 26)  # uniform 404 through get()

    with pytest.raises(AppError) as exc:
        await svc.create(key=f"d-{str(ULID()).lower()}", title="x",
                         domain="galaxy", layer_key="any",
                         owner_user_id=admin.id)
    assert exc.value.code == "VALIDATION_ERROR"
    with pytest.raises(AppError) as exc:
        await svc.create(key=f"d-{str(ULID()).lower()}", title="x",
                         domain="learning", layer_key="any",
                         owner_user_id=admin.id, risk_class="apocalyptic")
    assert exc.value.code == "VALIDATION_ERROR"
    with pytest.raises(AppError) as exc:
        await svc.create(key=f"d-{str(ULID()).lower()}", title="x",
                         domain="learning", layer_key="layer-does-not-exist",
                         owner_user_id=admin.id)
    assert exc.value.status_code == 404
    wrong_domain_layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="matching"
    )
    with pytest.raises(AppError) as exc:
        await svc.create(key=f"d-{str(ULID()).lower()}", title="x",
                         domain="learning", layer_key=wrong_domain_layer.key,
                         owner_user_id=admin.id)
    assert exc.value.code == "VALIDATION_ERROR"

    exp, _ = await _mk_running(db)
    # create_version only in draft/review
    with pytest.raises(AppError) as exc:
        await svc.create_version(exp.id, spec=_spec(), actor=admin)
    assert exc.value.code == "EXPERIMENT_INVALID_TRANSITION"
    # ramp refused in terminal statuses
    await svc.transition(exp.id, to_status="completed", actor=admin)
    with pytest.raises(AppError) as exc:
        await svc.set_ramp(exp.id, ramp_bp=100, actor=admin)
    assert exc.value.code == "EXPERIMENT_INVALID_TRANSITION"

    # schedule gates: no version, then incomplete checklist
    layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="learning"
    )
    bare = await svc.create(key=f"b-{str(ULID()).lower()}", title="B",
                            domain="learning", layer_key=layer.key,
                            owner_user_id=admin.id)
    await svc.transition(bare.id, to_status="review", actor=admin)
    with pytest.raises(AppError) as exc:
        await svc.transition(bare.id, to_status="scheduled", actor=admin,
                             checklist=_CHECKLIST)
    assert exc.value.code == "EXPERIMENT_SPEC_INVALID"
    await svc.transition(bare.id, to_status="draft", actor=admin)
    await svc.create_version(bare.id, spec=_spec(), actor=admin)
    await LayerService(db).allocate(layer_key=layer.key, experiment_id=bare.id,
                                    slice_start=0, slice_end=9999)
    await svc.transition(bare.id, to_status="review", actor=admin)
    with pytest.raises(AppError) as exc:
        await svc.transition(bare.id, to_status="scheduled", actor=admin,
                             checklist={"hypothesis_peer_checked": True})
    assert exc.value.code == "EXPERIMENT_CHECKLIST_INCOMPLETE"

    # spec not JSON-serializable -> typed 422
    with pytest.raises(AppError) as exc:
        await svc.create_version(bare.id, spec={**_spec(),
                                                "population": {"rules": []},
                                                "hypothesis": "x" * 20,
                                                "metrics": {"primary": ["exposure_rate"],
                                                            "guardrails": []},
                                                "_bad": float("inf")},
                                 actor=admin)
    assert exc.value.code in ("EXPERIMENT_SPEC_INVALID", "VALIDATION_ERROR")

    # search: filters + delegation scope + keyset cursor + events
    rows, total, _cursor = await svc.list_experiments(
        status="completed", domain="learning")
    assert any(r.id == exp.id for r in rows) and total >= 1
    scoped_rows, _, _ = await svc.list_experiments(scope_org_ids=["z" * 26])
    assert all(r.scope_org_id == "z" * 26 for r in scoped_rows)
    page1, _, cur = await svc.list_experiments(limit=1)
    if cur:
        page2, _, _ = await svc.list_experiments(limit=1, cursor=cur)
        assert all(r.id < page1[0].id for r in page2)
    events = await svc.list_events(exp.id, limit=5)
    assert events and all(e.experiment_id == exp.id for e in events)


async def test_clone_duplicates_spec_as_new_draft(db):
    """Round 92: clone = NEW draft carrying the source's current spec as v1
    (same spec hash), no layer allocation, audit-linked; a source without a
    version refuses typed; the key collision is the usual 409."""
    from app.experiments.models import ExperimentEvent, ExperimentVersion

    exp, _ = await _mk_running(db)
    svc = ExperimentService(db)
    admin = await _mk_admin(db)
    new_key = f"copy-{str(ULID()).lower()}"
    copy = await svc.clone(exp.id, new_key=new_key, actor=admin)
    assert copy.status == "draft"
    assert copy.key == new_key
    assert copy.title.endswith("(copy)")
    assert copy.layer_key == exp.layer_key
    src_v = (
        await db.execute(
            select(ExperimentVersion).where(
                ExperimentVersion.experiment_id == exp.id,
                ExperimentVersion.version == 1,
            )
        )
    ).scalar_one()
    copy_v = (
        await db.execute(
            select(ExperimentVersion).where(
                ExperimentVersion.experiment_id == copy.id,
                ExperimentVersion.version == 1,
            )
        )
    ).scalar_one()
    assert copy_v.spec_hash == src_v.spec_hash  # identical canonical spec
    from app.experiments.models import ExperimentLayerAllocation

    alloc = (
        await db.execute(
            select(ExperimentLayerAllocation).where(
                ExperimentLayerAllocation.experiment_id == copy.id
            )
        )
    ).scalar_one_or_none()
    assert alloc is None  # slices are claimed deliberately, never copied
    events = (
        await db.execute(
            select(ExperimentEvent).where(
                ExperimentEvent.experiment_id == copy.id,
                ExperimentEvent.event_type == "cloned_from",
            )
        )
    ).scalars().all()
    assert events and events[0].payload["source_experiment_id"] == exp.id

    # a version-less source refuses typed
    layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="learning"
    )
    bare = await svc.create(key=f"bare-{str(ULID()).lower()}", title="B",
                            domain="learning", layer_key=layer.key,
                            owner_user_id=admin.id)
    with pytest.raises(AppError) as exc:
        await svc.clone(bare.id, new_key=f"c-{str(ULID()).lower()}", actor=admin)
    assert exc.value.code == "EXPERIMENT_SPEC_INVALID"


async def test_list_experiments_text_search(db):
    """Round 93: q matches key OR title case-insensitively, and ILIKE
    wildcards in the user's input are literals (percent means percent)."""
    admin = await _mk_admin(db)
    svc = ExperimentService(db)
    layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="learning"
    )
    tag = str(ULID()).lower()[:10]
    by_key = await svc.create(key=f"needle-{tag}", title="Plain title",
                              domain="learning", layer_key=layer.key,
                              owner_user_id=admin.id)
    by_title = await svc.create(key=f"other-{tag}x", title=f"NEEDLE-{tag} inside",
                                domain="learning", layer_key=layer.key,
                                owner_user_id=admin.id)
    pct = await svc.create(key=f"pct-{tag}", title=f"100% ramp {tag}",
                           domain="learning", layer_key=layer.key,
                           owner_user_id=admin.id)

    rows, total, _ = await svc.list_experiments(q=f"needle-{tag}")
    ids = {r.id for r in rows}
    assert by_key.id in ids and by_title.id in ids and pct.id not in ids
    assert total == 2

    # literal percent — not a wildcard
    rows2, total2, _ = await svc.list_experiments(q=f"100% ramp {tag}")
    assert {r.id for r in rows2} == {pct.id} and total2 == 1
    # a bare % must NOT match everything with this tag
    rows3, _, _ = await svc.list_experiments(q=f"%{tag}%")
    assert rows3 == []


async def test_read_scope_dep_arms(db):
    """Round 107: the dep layer's own arms — check_enum's typed 422,
    experiment_read_scope's 403 for a plain user with no admin org
    memberships, the delegated org-ids path, and the self-serve pass-through
    (the caller IS the unit)."""
    from app.controlplane.models.tenant import TenantAccount
    from app.experiments.api.deps import (
        check_enum,
        experiment_read_scope,
        require_self_serve_user,
    )
    from app.models.organization import Organization, OrgMember, OrgRole

    with pytest.raises(AppError) as exc:
        check_enum("galaxy", frozenset({"learning"}), "domain")
    assert exc.value.status_code == 422 and "galaxy" in exc.value.message
    check_enum(None, frozenset({"learning"}), "domain")  # absent filter: fine

    plain = User(email=f"plain-{ULID()}@example.com", display_name="P",
                 role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(plain)
    await db.flush()
    with pytest.raises(AppError) as exc:
        await experiment_read_scope(user=plain, db=db)
    assert exc.value.status_code == 403

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}",
                           slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(name="dep", slug=f"dep-{str(ULID()).lower()}",
                       tenant_id=tenant.id)
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=plain.id, role=OrgRole.ADMIN))
    await db.flush()
    scope = await experiment_read_scope(user=plain, db=db)
    assert scope.org_ids == [org.id]

    admin = await _mk_admin(db)
    assert (await experiment_read_scope(user=admin, db=db)).org_ids is None
    assert (await require_self_serve_user(user=plain)) is plain


# ── §4.17 identity resolution (round 210) ────────────────────────────


async def test_identity_link_migrates_anonymous_history(db):
    """An unlinked anonymous id resolves as a user-typed unit; linking
    migrates its assignment IN PLACE (variant/bucket/assigned_at intact)
    and both id forms serve the same experience afterwards."""
    from sqlalchemy import select as _select

    exp, admin = await _mk_running(db)
    svc = AssignmentService(db)
    anon_id = str(ULID())

    first = await svc.resolve(experiment_key=exp.key,
                              unit_type="anonymous", unit_id=anon_id)
    assert first is not None
    again = await svc.resolve(experiment_key=exp.key,
                              unit_type="anonymous", unit_id=anon_id)
    assert again is not None and again.variant_key == first.variant_key

    user = User(email=f"idl-{ULID()}@example.com", display_name="L",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.flush()
    pre_row = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.unit_id == anon_id))
    ).scalar_one()
    original_assigned_at = pre_row.assigned_at

    out = await svc.link_identity(anonymous_id=anon_id, user_id=user.id)
    assert out["migrated"] == 1 and out["conflicts"] == 0

    migrated_row = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.unit_id == user.id))
    ).scalar_one()
    assert migrated_row.variant_key == first.variant_key
    assert migrated_row.assigned_at == original_assigned_at  # ITT intact
    gone = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.unit_id == anon_id))
    ).scalar_one_or_none()
    assert gone is None

    # both id forms now serve the user's assignment
    via_anon = await svc.resolve(experiment_key=exp.key,
                                 unit_type="anonymous", unit_id=anon_id)
    via_user = await svc.resolve(experiment_key=exp.key,
                                 unit_type="user", unit_id=user.id)
    assert via_anon is not None and via_user is not None
    assert via_anon.variant_key == first.variant_key
    assert via_user.variant_key == first.variant_key

    # idempotent re-link; rebinding to a DIFFERENT user refused
    out2 = await svc.link_identity(anonymous_id=anon_id, user_id=user.id)
    assert out2["migrated"] == 0 and out2["conflicts"] == 0
    other = User(email=f"idl2-{ULID()}@example.com", display_name="O",
                 role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(other)
    await db.flush()
    from app.exceptions import AppError as _AppError
    with pytest.raises(_AppError) as exc:
        await svc.link_identity(anonymous_id=anon_id, user_id=other.id)
    assert exc.value.code == "EXPERIMENT_IDENTITY_CONFLICT"
    assert exc.value.status_code == 422


async def test_identity_link_conflict_keeps_user_row_and_audits(db):
    """When BOTH ids were assigned in the same experiment, the user row
    stays authoritative, the anon row is removed, and the
    experiment_identity_conflict event records both variants."""
    from sqlalchemy import select as _select

    from app.experiments.models.audit import ExperimentEvent

    exp, admin = await _mk_running(db)
    svc = AssignmentService(db)
    anon_id = str(ULID())
    user = User(email=f"idc-{ULID()}@example.com", display_name="C",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.flush()

    via_anon = await svc.resolve(experiment_key=exp.key,
                                 unit_type="anonymous", unit_id=anon_id)
    via_user = await svc.resolve(experiment_key=exp.key,
                                 unit_type="user", unit_id=user.id)
    assert via_anon is not None and via_user is not None
    # an exposure recorded under the ANON id before the link (#74 setup)
    recorded = await svc.record_exposure(
        experiment_key=exp.key, unit_type="anonymous", unit_id=anon_id,
        dedup_key=f"idc-{anon_id}")
    assert recorded is True  # #75: the anon namespace records exposures

    out = await svc.link_identity(anonymous_id=anon_id, user_id=user.id)
    assert out["migrated"] == 0 and out["conflicts"] == 1

    kept = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.unit_id == user.id))
    ).scalar_one()
    assert kept.variant_key == via_user.variant_key
    event = (
        await db.execute(_select(ExperimentEvent).where(
            ExperimentEvent.experiment_id == exp.id,
            ExperimentEvent.event_type == "experiment_identity_conflict"))
    ).scalar_one()
    assert event.payload["anon_variant"] == via_anon.variant_key
    assert event.payload["user_variant"] == via_user.variant_key

    # the anon id now serves the USER's variant (one person, one
    # experience — even where the histories disagreed)
    after = await svc.resolve(experiment_key=exp.key,
                              unit_type="anonymous", unit_id=anon_id)
    assert after is not None and after.variant_key == via_user.variant_key

    # #74: the anon row's exposures SURVIVED the conflict deletion,
    # re-pointed at the surviving user assignment (append-only contract)
    from app.experiments.models import ExperimentExposure
    exposure_rows = (
        await db.execute(_select(ExperimentExposure).where(
            ExperimentExposure.experiment_id == exp.id))
    ).scalars().all()
    assert len(exposure_rows) == 1
    assert exposure_rows[0].assignment_id == kept.id

    # malformed anonymous ids refuse — status pinned at BOTH raise sites
    # (the two-raise-sites-two-pins law)
    from app.exceptions import AppError as _AppError
    with pytest.raises(_AppError) as too_long:
        await svc.link_identity(anonymous_id="x" * 27, user_id=user.id)
    assert too_long.value.status_code == 422
    with pytest.raises(_AppError) as has_colon:
        await svc.link_identity(anonymous_id="a:b", user_id=user.id)
    assert has_colon.value.status_code == 422

    # boundary: a SINGLE-char id is admissible (the floor is 1, inclusive)
    one = await svc.link_identity(anonymous_id="z", user_id=user.id)
    assert one["anonymous_id"] == "z" and one["conflicts"] == 0


async def test_identity_link_racing_resolve_not_stranded(db, monkeypatch):
    """#73 (round 213): a link landing BETWEEN resolve's forward-check and
    its insert must not strand an orphan anon-keyed row — the post-insert
    re-check migrates it immediately, so one person holds one row and both
    id forms serve the same variant."""
    from sqlalchemy import select as _select

    exp, admin = await _mk_running(db)
    svc = AssignmentService(db)
    anon_id = str(ULID())
    user = User(email=f"idr-{ULID()}@example.com", display_name="R",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.flush()

    original_compute = AssignmentService.compute
    fired = {"done": False}

    async def racing_compute(self, **kwargs):
        out = await original_compute(self, **kwargs)
        if not fired["done"]:
            fired["done"] = True
            # the link lands in the race window (forward-check already
            # passed, insert not yet written)
            await AssignmentService(self.db).link_identity(
                anonymous_id=anon_id, user_id=user.id
            )
        return out

    monkeypatch.setattr(AssignmentService, "compute", racing_compute)
    resolved = await svc.resolve(
        experiment_key=exp.key, unit_type="anonymous", unit_id=anon_id
    )
    assert resolved is not None

    orphan = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.unit_id == anon_id))
    ).scalar_one_or_none()
    assert orphan is None  # the race window closed behind us
    user_row = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.unit_id == user.id))
    ).scalar_one()
    assert user_row.variant_key == resolved.variant_key

    monkeypatch.setattr(AssignmentService, "compute", original_compute)
    via_user = await svc.resolve(
        experiment_key=exp.key, unit_type="user", unit_id=user.id
    )
    via_anon = await svc.resolve(
        experiment_key=exp.key, unit_type="anonymous", unit_id=anon_id
    )
    assert via_user is not None and via_anon is not None
    assert via_user.variant_key == resolved.variant_key
    assert via_anon.variant_key == resolved.variant_key


async def test_identity_link_racing_switchback_not_stranded(db, monkeypatch):
    """Round 215: #73's race window exists around the SWITCHBACK placeholder
    insert too — the mirror re-check migrates the placeholder so the ITT
    roster holds one row for the person."""
    from sqlalchemy import select as _select

    exp, admin = await _mk_running(
        db, spec_overrides={"design": "switchback",
                            "switchback": {"switch_unit": "platform_day",
                                           "window_minutes": 1440}})
    svc = AssignmentService(db)
    anon_id = str(ULID())
    user = User(email=f"idsw-{ULID()}@example.com", display_name="S",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.flush()

    original_compute = AssignmentService.compute
    fired = {"done": False}

    async def racing_compute(self, **kwargs):
        out = await original_compute(self, **kwargs)
        if not fired["done"]:
            fired["done"] = True
            await AssignmentService(self.db).link_identity(
                anonymous_id=anon_id, user_id=user.id
            )
        return out

    monkeypatch.setattr(AssignmentService, "compute", racing_compute)
    resolved = await svc.resolve(
        experiment_key=exp.key, unit_type="anonymous", unit_id=anon_id
    )
    assert resolved is not None  # the day's variant serves

    orphan = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.unit_id == anon_id))
    ).scalar_one_or_none()
    assert orphan is None
    user_row = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.unit_id == user.id))
    ).scalar_one()
    assert user_row is not None  # exactly one roster row for the person

    # wave-41 killer: the served CONFIG belongs to the day's variant —
    # a flipped lookup serves another variant's payload
    expected_config = ({"rubric_template_id": "x"}
                       if resolved.variant_key == "treatment" else {})
    assert resolved.config == expected_config


async def test_identity_link_cascades_with_user_deletion(db):
    """Round 222 (exp16): the anon<->user mapping is privacy-relevant —
    deleting the user deletes their identity links too, never an orphan."""
    from sqlalchemy import select as _select

    from app.experiments.models import ExperimentIdentityLink

    svc = AssignmentService(db)
    user = User(email=f"idd-{ULID()}@example.com", display_name="D",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.flush()
    anon_id = str(ULID())
    await svc.link_identity(anonymous_id=anon_id, user_id=user.id)

    await db.delete(user)
    await db.flush()
    gone = (
        await db.execute(_select(ExperimentIdentityLink).where(
            ExperimentIdentityLink.anonymous_id == anon_id))
    ).scalar_one_or_none()
    assert gone is None


async def test_exposure_racing_link_conflict_lands_on_survivor(db, monkeypatch):
    """#76 (round 223): an exposure in flight when the identity-link
    CONFLICT fold deletes its anon assignment row must not be lost — the
    nested-savepoint retry re-normalizes and attaches it to the surviving
    user assignment."""
    from sqlalchemy import select as _select

    from app.experiments.models import ExperimentExposure

    exp, admin = await _mk_running(db)
    svc = AssignmentService(db)
    anon_id = str(ULID())
    user = User(email=f"idx-{ULID()}@example.com", display_name="X",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.flush()
    # both ids assigned -> a later link takes the CONFLICT fold
    assert await svc.resolve(experiment_key=exp.key,
                             unit_type="anonymous", unit_id=anon_id)
    assert await svc.resolve(experiment_key=exp.key,
                             unit_type="user", unit_id=user.id)

    original_existing = AssignmentService._existing
    fired = {"done": False}

    async def racing_existing(self, experiment_id, unit_type, unit_id):
        row = await original_existing(self, experiment_id, unit_type, unit_id)
        if not fired["done"] and unit_id == anon_id:
            fired["done"] = True
            # the link lands AFTER the exposure's assignment lookup —
            # the conflict fold deletes the row the exposure points at
            await AssignmentService(self.db).link_identity(
                anonymous_id=anon_id, user_id=user.id
            )
        return row

    monkeypatch.setattr(AssignmentService, "_existing", racing_existing)
    recorded = await svc.record_exposure(
        experiment_key=exp.key, unit_type="anonymous", unit_id=anon_id,
        dedup_key=f"race-{anon_id}")
    assert recorded is True  # never silently lost
    monkeypatch.setattr(AssignmentService, "_existing", original_existing)

    survivor = await svc._existing(exp.id, "user", user.id)
    rows = (
        await db.execute(_select(ExperimentExposure).where(
            ExperimentExposure.experiment_id == exp.id,
            ExperimentExposure.dedup_key == f"race-{anon_id}"))
    ).scalars().all()
    assert len(rows) == 1
    assert rows[0].assignment_id == survivor.id


async def test_link_conflict_survives_dedup_key_collision(db):
    """#78 (round 251): BOTH identities recorded an exposure under the SAME
    dedup key before the link — the conflict fold's exposure re-point must
    not violate the per-assignment dedup unique (the colliding anon row is
    a semantic duplicate and folds away); the link succeeds and exactly one
    exposure with that key survives on the user assignment."""
    from sqlalchemy import select as _select

    from app.experiments.models import ExperimentExposure

    exp, admin = await _mk_running(db)
    svc = AssignmentService(db)
    anon_id = str(ULID())
    user = User(email=f"idk-{ULID()}@example.com", display_name="K",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.flush()
    assert await svc.resolve(experiment_key=exp.key,
                             unit_type="anonymous", unit_id=anon_id)
    assert await svc.resolve(experiment_key=exp.key,
                             unit_type="user", unit_id=user.id)
    # the same client-side natural key lands under BOTH identities
    shared_key = f"day-{anon_id[:8]}"
    assert await svc.record_exposure(
        experiment_key=exp.key, unit_type="anonymous", unit_id=anon_id,
        dedup_key=shared_key) is True
    assert await svc.record_exposure(
        experiment_key=exp.key, unit_type="user", unit_id=user.id,
        dedup_key=shared_key, context={"side": "user"}) is True
    # a second anon exposure with a NON-colliding key must survive the fold
    assert await svc.record_exposure(
        experiment_key=exp.key, unit_type="anonymous", unit_id=anon_id,
        dedup_key=f"unique-{anon_id[:8]}") is True

    out = await svc.link_identity(anonymous_id=anon_id, user_id=user.id)
    assert out["conflicts"] == 1  # the fold itself succeeded

    survivor = await svc._existing(exp.id, "user", user.id)
    rows = (
        await db.execute(_select(ExperimentExposure).where(
            ExperimentExposure.experiment_id == exp.id))
    ).scalars().all()
    assert all(r.assignment_id == survivor.id for r in rows)
    shared = [r for r in rows if r.dedup_key == shared_key]
    unique = [r for r in rows if r.dedup_key == f"unique-{anon_id[:8]}"]
    assert len(shared) == 1   # the colliding duplicate folded away
    # the SURVIVOR's physical row is the one that remains — the fold
    # deletes the anon duplicate, never the user's original
    assert shared[0].context == {"side": "user"}
    assert len(unique) == 1   # the non-colliding exposure re-pointed


async def test_link_migration_racing_user_resolve(db, monkeypatch):
    """#79 (round 254, the #78 class generalized): the migration's
    check-then-UPDATE races a concurrent resolve that creates the user row
    between them — the unique constraint fired and the whole link 500'd.
    The per-row nested savepoint retries through the conflict branch: the
    user row wins, the anon row folds with the audit event."""
    from sqlalchemy import select as _select

    from app.experiments.models.audit import ExperimentEvent

    exp, admin = await _mk_running(db)
    svc = AssignmentService(db)
    anon_id = str(ULID())
    user = User(email=f"idm-{ULID()}@example.com", display_name="M",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.flush()
    anon_resolved = await svc.resolve(
        experiment_key=exp.key, unit_type="anonymous", unit_id=anon_id)
    assert anon_resolved is not None

    original_existing = AssignmentService._existing
    fired = {"done": False}

    async def racing_existing(self, experiment_id, unit_type, unit_id):
        row = await original_existing(self, experiment_id, unit_type, unit_id)
        if not fired["done"] and unit_id == user.id and row is None:
            fired["done"] = True
            # the user resolves themselves INSIDE the race window — their
            # row lands after the migration's existence check
            await AssignmentService(self.db).resolve(
                experiment_key=exp.key, unit_type="user", unit_id=user.id)
        return row

    monkeypatch.setattr(AssignmentService, "_existing", racing_existing)
    out = await svc.link_identity(anonymous_id=anon_id, user_id=user.id)
    monkeypatch.setattr(AssignmentService, "_existing", original_existing)
    assert out["conflicts"] == 1 and out["migrated"] == 0

    rows = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.unit_id.in_([anon_id, user.id])))
    ).scalars().all()
    assert len(rows) == 1 and rows[0].unit_id == user.id
    event = (
        await db.execute(_select(ExperimentEvent).where(
            ExperimentEvent.experiment_id == exp.id,
            ExperimentEvent.event_type == "experiment_identity_conflict"))
    ).scalar_one()
    assert event.payload["anonymous_id"] == anon_id


async def test_layer_service_negative_paths(db):
    """Round 369 (coverage map): the LayerService guard branches —
    unknown domain, duplicate key, missing layer, slice validations and
    the one-allocation-per-experiment constraint — pinned at the service
    seam (the wall exercises them over HTTP, outside pytest-cov)."""
    import pytest as _pytest

    from app.exceptions import AppError
    from app.experiments.services.layers import LayerService

    svc = LayerService(db)
    with _pytest.raises(AppError) as e:
        await svc.create(key=f"neg-{str(ULID()).lower()}", domain="nope")
    assert e.value.code == "VALIDATION_ERROR"

    key = f"neg-{str(ULID()).lower()}"
    await svc.create(key=key, domain="learning")
    try:
        async with db.begin_nested():
            with _pytest.raises(AppError) as e:
                await svc.create(key=key, domain="learning")
    except Exception:  # noqa: BLE001 — savepoint absorbs the poisoned flush
        pass
    assert e.value.code == "EXPERIMENT_KEY_TAKEN"

    with _pytest.raises(AppError) as e:
        await svc.allocate(layer_key="layer-that-is-not-" + key,
                           experiment_id="x" * 26,
                           slice_start=0, slice_end=1)
    assert e.value.code == "EXPERIMENT_NOT_FOUND"

    admin = await _mk_admin(db)
    from app.experiments.services.experiments import ExperimentService

    exp = await ExperimentService(db).create(
        key=f"neg-exp-{str(ULID()).lower()}", title="N", domain="learning",
        layer_key=key, owner_user_id=admin.id,
    )
    with _pytest.raises(AppError) as e:
        await svc.allocate(layer_key=key, experiment_id=exp.id,
                           slice_start=5, slice_end=4)
    assert e.value.code == "VALIDATION_ERROR"
    with _pytest.raises(AppError) as e:
        await svc.allocate(layer_key=key, experiment_id=exp.id,
                           slice_start=0, slice_end=10_000)
    assert e.value.code == "VALIDATION_ERROR"
    with _pytest.raises(AppError) as e:
        await svc.allocate(layer_key=key, experiment_id="x" * 26,
                           slice_start=0, slice_end=1)
    assert e.value.code == "EXPERIMENT_NOT_FOUND"
    other_key = f"neg2-{str(ULID()).lower()}"
    await svc.create(key=other_key, domain="learning")
    with _pytest.raises(AppError) as e:
        await svc.allocate(layer_key=other_key, experiment_id=exp.id,
                           slice_start=0, slice_end=1)
    assert e.value.code == "VALIDATION_ERROR"  # belongs to another layer

    await svc.allocate(layer_key=key, experiment_id=exp.id,
                       slice_start=0, slice_end=99)
    try:
        async with db.begin_nested():
            with _pytest.raises(AppError) as e:
                await svc.allocate(layer_key=key, experiment_id=exp.id,
                                   slice_start=100, slice_end=199)
    except Exception:  # noqa: BLE001
        pass
    assert e.value.code == "LAYER_SLICE_OVERLAP"


async def test_identity_link_per_user_cap(db, monkeypatch):
    """Defect #98: link_identity had no per-user cap — a hostile
    authenticated caller could write unbounded rows into the GLOBAL link
    table (storage amplification; each POST also runs migration scans).
    Contract: at the cap a NEW link is 422 EXPERIMENT_IDENTITY_LINK_CAP,
    while re-linking an EXISTING pair stays idempotent-OK."""
    import pytest as _pytest

    import app.experiments.services.assignment as asg
    from app.exceptions import AppError as _AppError

    _, admin = await _mk_running(db)
    svc = AssignmentService(db)
    user = User(email=f"cap98-{ULID()}@example.com", display_name="C",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.flush()

    monkeypatch.setattr(asg, "IDENTITY_LINK_CAP_PER_USER", 3, raising=False)
    anons = [str(ULID()) for _ in range(3)]
    for a in anons:
        await svc.link_identity(anonymous_id=a, user_id=user.id)
    # 4th NEW link: refused at the cap
    with _pytest.raises(_AppError) as e:
        await svc.link_identity(anonymous_id=str(ULID()), user_id=user.id)
    assert e.value.code == "EXPERIMENT_IDENTITY_LINK_CAP"
    # Re-linking an existing pair is still idempotent at the cap
    out = await svc.link_identity(anonymous_id=anons[0], user_id=user.id)
    assert out is not None


async def test_identity_link_cap_holds_under_concurrency(db, monkeypatch):
    """Defect #101 (#100's twin): the #98 cap check was a bare COUNT — two
    concurrent transactions both read cap-1 and both inserted. The fix
    locks the User row (FOR UPDATE) before counting so link writers for
    the same user serialize and the cap is exact."""
    import asyncio as _aio
    import contextlib as _ctx

    import app.experiments.services.assignment as asg
    from app.exceptions import AppError as _AppError

    user = User(email=f"c101-{ULID()}@example.com", display_name="R",
                role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(user)
    await db.commit()  # writer sessions must SEE the user
    monkeypatch.setattr(asg, "IDENTITY_LINK_CAP_PER_USER", 1, raising=False)

    # Overlap gate BETWEEN link_identity and commit: both writers must pass
    # the COUNT before either commits. With the FOR-UPDATE fix the second
    # writer blocks inside link_identity at the user-row lock, never reaches
    # the gate, and the first times out and proceeds.
    gate = _aio.Event()
    arrived: list[int] = []
    run_tag = str(ULID()).lower()[:10]

    async def gated_writer(tag: str) -> bool:
        async with AsyncSessionLocal() as s:
            svc = AssignmentService(s)
            try:
                await svc.link_identity(anonymous_id=f"c101{run_tag}{tag}", user_id=user.id)
                arrived.append(1)
                if len(arrived) >= 2:
                    gate.set()
                with _ctx.suppress(TimeoutError):
                    await _aio.wait_for(gate.wait(), timeout=1.0)
                await s.commit()
                return True
            except _AppError:
                await s.rollback()
                return False

    results = await _aio.gather(gated_writer("a"), gated_writer("b"))
    assert sum(results) == 1, f"exactly one link may land at cap=1, got {results}"
    from sqlalchemy import delete as _delete
    from sqlalchemy import func as _func

    from app.experiments.models import ExperimentIdentityLink as _Lnk

    n = (
        await db.execute(
            select(_func.count()).select_from(_Lnk).where(_Lnk.user_id == user.id)
        )
    ).scalar_one()
    assert n == 1, f"cap must be exact under concurrency, found {n} links"
    # cleanup: this test commits — remove the links it created
    await db.execute(_delete(_Lnk).where(_Lnk.user_id == user.id))
    await db.commit()
