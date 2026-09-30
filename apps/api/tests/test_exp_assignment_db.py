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
from app.experiments.models import (
    Experiment,
    ExperimentAssignment,
    ExperimentLayer,
    ExperimentLayerAllocation,
)
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.layers import LayerService
from app.models.user import User, UserRole, UserStatus


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
    await svc.transition(exp.id, to_status="scheduled", actor=admin)
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
