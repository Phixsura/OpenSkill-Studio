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
        "EXPERIMENT_NO_GUARDRAILS": {422},
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
