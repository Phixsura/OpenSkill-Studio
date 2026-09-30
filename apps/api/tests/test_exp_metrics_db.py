"""Metric definitions/snapshots DB tests (ADR-017 exp03).

Seed idempotency, definition validation, ITT variant-unit grouping (holdouts
excluded), the exposures source end-to-end, snapshot UPSERT recompute with
provenance, unwired-source skip, and the outbox sweep enqueue path.

Runs against the dev Postgres (exp03 applied); rollback-per-test.
"""

from datetime import UTC, datetime, time, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.exceptions import AppError
from app.experiments.models import MetricSnapshot
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.layers import LayerService
from app.experiments.services.metrics import (
    SEED_METRIC_DEFINITIONS,
    SOURCE_REGISTRY,
    MetricService,
)
from app.experiments.worker import previous_utc_day, sweep_experiment_windows
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def _spec() -> dict:
    return {
        "hypothesis": "exposure-rate metric machinery works end to end",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {
            "primary": ["exposure_rate"],
            "secondary": ["project_approval_rate"],  # source unwired until exp07
            "guardrails": [{"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}],
        },
    }


async def _mk_admin(db) -> User:
    user = User(
        email=f"exp-metric-{ULID()}@example.com",
        display_name="M",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_running(db):
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}",
        title="T",
        domain="learning",
        layer_key=layer.key,
        owner_user_id=admin.id,
    )
    await svc.create_version(exp.id, spec=_spec(), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    return exp, admin


def _today_window() -> tuple[datetime, datetime]:
    start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    return start, start + timedelta(days=1)


# ── Definitions ──────────────────────────────────────────────────────


async def test_seed_definitions_idempotent(db):
    svc = MetricService(db)
    first = await svc.ensure_seed_definitions()
    second = await svc.ensure_seed_definitions()
    assert second == 0
    keys = {d.key for d in await svc.list_definitions()}
    assert {s["key"] for s in SEED_METRIC_DEFINITIONS} <= keys
    assert first <= len(SEED_METRIC_DEFINITIONS)


async def test_create_definition_validates_enums(db):
    svc = MetricService(db)
    with pytest.raises(AppError) as e:
        await svc.create_definition(
            key=f"m_{str(ULID()).lower()}", title="x", kind="bogus",
            domain="learning", source_kind="service",
        )
    assert "kind" in e.value.message


async def test_create_definition_duplicate_key_409(db):
    svc = MetricService(db)
    key = f"m_{str(ULID()).lower()}"
    await svc.create_definition(
        key=key, title="x", kind="binary", domain="learning", source_kind="service"
    )
    with pytest.raises(AppError) as e:
        await svc.create_definition(
            key=key, title="x", kind="binary", domain="learning", source_kind="service"
        )
    assert e.value.code == "EXPERIMENT_KEY_TAKEN"


# ── Snapshot computation ─────────────────────────────────────────────


async def test_exposures_source_end_to_end_with_provenance(db):
    await MetricService(db).ensure_seed_definitions()
    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    exposed_variants = set()
    for i in range(30):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"m-{i}")
        assert r is not None
        if i % 2 == 0:
            await asvc.record_exposure(
                experiment_key=exp.key, unit_type="user", unit_id=f"m-{i}"
            )
            exposed_variants.add(r.variant_key)

    window_start, window_end = _today_window()
    written = await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    # exposure_rate for each variant; unwired sources skipped
    assert written == 2
    snapshots = await MetricService(db).list_snapshots(exp.id)
    assert {s.metric_key for s in snapshots} == {"exposure_rate"}
    total_exposed = sum(int(s.numerator or 0) for s in snapshots)
    assert total_exposed == 15
    total_assigned = sum(int(s.denominator or 0) for s in snapshots)
    assert total_assigned == 30
    for s in snapshots:
        assert s.provenance["source"] == "exposures"
        assert s.provenance["query_version"] == 1


async def test_snapshot_recompute_upserts_same_window(db):
    await MetricService(db).ensure_seed_definitions()
    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id="u1-recompute")
    window_start, window_end = _today_window()
    msvc = MetricService(db)
    await msvc.compute_experiment_window(exp.id, window_start=window_start, window_end=window_end)
    before = len(await msvc.list_snapshots(exp.id))
    # New exposure lands, recompute the SAME window — row count must not grow
    await asvc.record_exposure(experiment_key=exp.key, unit_type="user", unit_id="u1-recompute")
    await msvc.compute_experiment_window(exp.id, window_start=window_start, window_end=window_end)
    after = await msvc.list_snapshots(exp.id)
    assert len(after) == before
    exposed = sum(int(s.numerator or 0) for s in after if s.metric_key == "exposure_rate")
    assert exposed == 1


async def test_holdout_units_excluded_from_itt_sets(db):
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id, holdout_bp=1000,
    )
    await svc.create_version(exp.id, spec=_spec(), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    asvc = AssignmentService(db)
    held = 0
    for i in range(200):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"ho-{i}")
        held += r is None
    assert held > 0
    window_start, window_end = _today_window()
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    snapshots = await MetricService(db).list_snapshots(exp.id)
    assert sum(int(s.denominator or 0) for s in snapshots) == 200 - held


async def test_unwired_source_is_skipped_not_crashed(db):
    """project_approval_rate's source lands in exp07 — computing today must
    skip it (logged) and still write the wired metrics."""
    assert "projects" not in SOURCE_REGISTRY
    await MetricService(db).ensure_seed_definitions()
    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    for i in range(20):  # enough units to land in both variants
        await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"skip-{i}")
    window_start, window_end = _today_window()
    written = await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    assert written == 2  # exposure_rate × 2 variants only


# ── Worker sweep ─────────────────────────────────────────────────────


async def test_sweep_enqueues_yesterday_window_for_live_experiments(db):
    await MetricService(db).ensure_seed_definitions()
    exp, _ = await _mk_running(db)
    enqueued = await sweep_experiment_windows(db)
    assert enqueued >= 1
    from app.controlplane.models.outbox import OutboxMessage

    rows = list(
        (
            await db.execute(
                select(OutboxMessage).where(
                    OutboxMessage.topic == "exp.compute_snapshots",
                    OutboxMessage.status == "pending",
                )
            )
        ).scalars()
    )
    mine = [m for m in rows if m.payload.get("experiment_id") == exp.id]
    assert len(mine) == 1
    ws, we = previous_utc_day()
    assert mine[0].payload["window_start"] == ws.isoformat()
    assert mine[0].payload["window_end"] == we.isoformat()


async def test_sweep_skips_closed_analysis(db):
    exp, admin = await _mk_running(db)
    svc = ExperimentService(db)
    await svc.transition(exp.id, to_status="completed", actor=admin)
    exp.analysis_close_at = datetime.now(UTC) - timedelta(days=1)
    await db.flush()
    await sweep_experiment_windows(db)
    from app.controlplane.models.outbox import OutboxMessage

    rows = list(
        (
            await db.execute(
                select(OutboxMessage).where(OutboxMessage.topic == "exp.compute_snapshots")
            )
        ).scalars()
    )
    assert all(m.payload.get("experiment_id") != exp.id for m in rows)


async def test_snapshot_unique_constraint_names_window(db):
    """The UPSERT targets uq_experiment_metric_snapshots_window — pin the
    constraint name so a rename breaks loudly here, not silently in prod."""
    names = {c.name for c in MetricSnapshot.__table__.constraints}
    assert "uq_experiment_metric_snapshots_window" in names
