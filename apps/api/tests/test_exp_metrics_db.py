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
from app.experiments.security import ETHICS_CHECKLIST_KEY, LAUNCH_CHECKLIST_KEYS
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

_CHECKLIST = {key: True for key in (*LAUNCH_CHECKLIST_KEYS, ETHICS_CHECKLIST_KEY)}

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
            "secondary": ["completion_rate"],  # learning_paths derived source (batch 3)
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


async def _mk_running(db, *, extra_secondary: list[str] | None = None):
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
    spec = _spec()
    if extra_secondary:
        spec["metrics"]["secondary"] = spec["metrics"].get("secondary", []) + extra_secondary
    await svc.create_version(exp.id, spec=spec, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
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
    # exposure_rate + completion_rate (wired in batch 3, zero completions)
    # + cost_usd guardrail (zero-sample for user units), per variant
    assert written == 6
    snapshots = await MetricService(db).list_snapshots(exp.id)
    assert {s.metric_key for s in snapshots} == {
        "exposure_rate", "completion_rate", "cost_usd"
    }
    exposure_rows = [s for s in snapshots if s.metric_key == "exposure_rate"]
    total_exposed = sum(int(s.numerator or 0) for s in exposure_rows)
    assert total_exposed == 15
    total_assigned = sum(int(s.denominator or 0) for s in exposure_rows)
    assert total_assigned == 30
    for s in exposure_rows:
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


async def test_recompute_denominator_pinned_to_window_end(db):
    """Window-consistent ITT: recomputing yesterday's window after new units
    were assigned today must NOT dilute yesterday's denominator (units are
    filtered by assigned_at < window_end)."""
    from app.experiments.models import ExperimentAssignment

    await MetricService(db).ensure_seed_definitions()
    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    for i in range(10):
        await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"w-{i}")
        await asvc.record_exposure(experiment_key=exp.key, unit_type="user", unit_id=f"w-{i}")
    # Backdate these assignments+exposures into yesterday's window
    from sqlalchemy import update as _update

    from app.experiments.models import ExperimentExposure

    yesterday = datetime.now(UTC) - timedelta(days=1)
    await db.execute(
        _update(ExperimentAssignment)
        .where(ExperimentAssignment.experiment_id == exp.id)
        .values(assigned_at=yesterday)
    )
    await db.execute(
        _update(ExperimentExposure)
        .where(ExperimentExposure.experiment_id == exp.id)
        .values(occurred_at=yesterday)
    )
    window_start = datetime.combine(yesterday.date(), time.min, tzinfo=UTC)
    window_end = window_start + timedelta(days=1)
    msvc = MetricService(db)
    await msvc.compute_experiment_window(exp.id, window_start=window_start, window_end=window_end)
    first = {
        (s.variant_key): float(s.denominator or 0)
        for s in await msvc.list_snapshots(exp.id, metric_key="exposure_rate")
    }
    assert sum(first.values()) == 10
    # New units assigned TODAY, then recompute YESTERDAY's window
    for i in range(5):
        await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"today-{i}")
    await msvc.compute_experiment_window(exp.id, window_start=window_start, window_end=window_end)
    second = {
        (s.variant_key): float(s.denominator or 0)
        for s in await msvc.list_snapshots(exp.id, metric_key="exposure_rate")
    }
    assert second == first, "today's assignments diluted yesterday's denominator"


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
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
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
    exposure_rows = [s for s in snapshots if s.metric_key == "exposure_rate"]
    assert sum(int(s.denominator or 0) for s in exposure_rows) == 200 - held


async def test_every_seed_source_is_wired_and_unwired_skips(db):
    """v2 batch 3 closed the source gap: EVERY source a seed definition
    declares is registered (the unwired set is pinned empty). The skip-not-
    crash contract stays covered via a definition pointing at a source that
    does not exist."""
    from app.experiments.services.metrics import SEED_METRIC_DEFINITIONS

    declared = {d["spec"].get("source") for d in SEED_METRIC_DEFINITIONS}
    assert sorted(declared - set(SOURCE_REGISTRY)) == []

    svc = MetricService(db)
    await svc.ensure_seed_definitions()
    await svc.create_definition(
        key="ghost_metric", title="Ghost", kind="binary", domain="learning",
        source_kind="service", spec={"source": "no_such_source"},
    )
    exp, _ = await _mk_running(db, extra_secondary=["ghost_metric"])
    asvc = AssignmentService(db)
    for i in range(20):  # enough units to land in both variants
        await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"skip-{i}")
    window_start, window_end = _today_window()
    written = await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    # exposure_rate + completion_rate (now wired, zero-completion) + cost_usd
    # guardrail x 2 variants; ghost_metric skipped, not crashed
    assert written == 6


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


async def test_sweep_closed_analysis_never_occupies_cap_slots(db):
    """Fourth accumulation-bomb shape (§106.26): the close filter must live
    in SQL BEFORE the cap — an older analytically-closed experiment must not
    starve a live one out of a cap-1 sweep."""
    # §106.25: push any pre-existing sweep-eligible experiments (committed
    # residue in the shared dev DB) out of the window first — the in-txn
    # UPDATE is rolled back with the test.
    from sqlalchemy import update as _update

    from app.experiments.models import Experiment as _Exp

    await db.execute(
        _update(_Exp)
        .where(_Exp.status.in_(("running", "paused", "completed", "analyzed")))
        .values(analysis_close_at=datetime.now(UTC) - timedelta(days=1))
    )
    old_exp, old_admin = await _mk_running(db)
    svc = ExperimentService(db)
    await svc.transition(old_exp.id, to_status="completed", actor=old_admin)
    old_exp.analysis_close_at = datetime.now(UTC) - timedelta(days=1)
    await db.flush()
    live_exp, _ = await _mk_running(db)  # newer id → loses an id-ordered cap-1
    enqueued = await sweep_experiment_windows(db, cap=1)
    assert enqueued == 1
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
    mine = {m.payload["experiment_id"] for m in rows} & {old_exp.id, live_exp.id}
    assert mine == {live_exp.id}


async def test_closure_sweep_completes_past_max_days(db):
    from app.experiments.worker import sweep_experiment_closures

    exp, admin = await _mk_running(db)  # spec default max_days=28
    fresh_exp, _ = await _mk_running(db)
    exp_row = await ExperimentService(db).get(exp.id)
    exp_row.started_at = datetime.now(UTC) - timedelta(days=29)
    await db.flush()
    closed = await sweep_experiment_closures(db)
    assert closed >= 1
    assert (await ExperimentService(db).get(exp.id)).status == "completed"
    assert (await ExperimentService(db).get(exp.id)).analysis_close_at is not None
    # a fresh experiment is untouched
    assert (await ExperimentService(db).get(fresh_exp.id)).status == "running"


async def test_prune_deletes_only_archived_old_exposures(db):
    from datetime import UTC as _UTC
    from datetime import datetime as _dt

    from app.experiments.models import ExperimentExposure
    from app.experiments.services.assignment import AssignmentService
    from app.experiments.worker import prune_experiment_history

    await MetricService(db).ensure_seed_definitions()
    exp_live, _ = await _mk_running(db)
    exp_old, admin_old = await _mk_running(db)
    asvc = AssignmentService(db)
    for exp in (exp_live, exp_old):
        await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id="pr-1")
        await asvc.record_exposure(experiment_key=exp.key, unit_type="user", unit_id="pr-1")
    # age both exposures far past retention; archive only one experiment
    await db.execute(
        select(ExperimentExposure)  # noqa: F841 — force flush ordering
    )
    from sqlalchemy import update as _update

    await db.execute(
        _update(ExperimentExposure)
        .where(ExperimentExposure.experiment_id.in_((exp_live.id, exp_old.id)))
        .values(occurred_at=_dt(2020, 1, 1, tzinfo=_UTC))
    )
    await ExperimentService(db).transition(exp_old.id, to_status="archived", actor=admin_old)
    pruned = await prune_experiment_history(db)
    assert pruned["exposures"] >= 1
    remaining = list(
        (
            await db.execute(
                select(ExperimentExposure.experiment_id).where(
                    ExperimentExposure.experiment_id.in_((exp_live.id, exp_old.id))
                )
            )
        ).scalars()
    )
    assert exp_old.id not in remaining  # archived + old → pruned
    assert exp_live.id in remaining  # live experiments keep their trail


async def test_exp_sweeps_registered_in_cron_table():
    """The §96 guard class: sweeps that exist but are never scheduled are
    dead code — pin all three experiment sweeps into the worker cron
    registry by name."""
    from app.controlplane.worker import _cron_jobs

    names = {job.name for job in _cron_jobs()}
    assert {
        "exp_guardrail_sweep",
        "exp_window_sweep",
        "exp_closure_sweep",
        "exp_retention",
    } <= names


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


async def _mk_org(db):
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}", slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(
        name=f"o-{str(ULID()).lower()}", slug=f"o-{str(ULID()).lower()}", tenant_id=tenant.id
    )
    db.add(org)
    await db.flush()
    return tenant, org


def _units(variant_units_flat: list[str]) -> dict[str, list[str]]:
    return {"treatment": variant_units_flat}


async def _run_source(db, source_name: str, *, definition_key: str, units, unit_type: str):
    from sqlalchemy import select as _select

    from app.experiments.models import MetricDefinition
    from app.experiments.services.metrics import SOURCE_REGISTRY

    await MetricService(db).ensure_seed_definitions()
    definition = (
        await db.execute(_select(MetricDefinition).where(MetricDefinition.key == definition_key))
    ).scalar_one()
    window_start, window_end = _today_window()
    return await SOURCE_REGISTRY[source_name](
        db, experiment=None, definition=definition, variant_units=_units(units),
        window_start=window_start, window_end=window_end, unit_type=unit_type,
    )


# ── exp07 wired sources ──────────────────────────────────────────────


async def test_projects_source_approval_and_revisions(db):
    from app.models.project import Project, Submission, SubmissionStatus

    _tenant, org = await _mk_org(db)
    user = await _mk_admin(db)
    project = Project(
        org_id=org.id, title="P", slug=f"p-{str(ULID()).lower()}",
        description="d", instructions="i", rubric=[{"criterion": "c", "max_score": 5}],
    )
    db.add(project)
    await db.flush()
    for status, version in (
        (SubmissionStatus.APPROVED, 3),  # 2 revisions
        (SubmissionStatus.APPROVED, 1),
        (SubmissionStatus.REJECTED, 2),  # 1 revision
    ):
        db.add(
            Submission(org_id=org.id, project_id=project.id, user_id=user.id,
                       status=status, version=version)
        )
    await db.flush()
    approval = await _run_source(
        db, "projects", definition_key="project_approval_rate",
        units=[user.id], unit_type="user",
    )
    assert approval["treatment"] == {"n": 3, "numerator": 2, "denominator": 3}
    revisions = await _run_source(
        db, "projects", definition_key="revision_count", units=[user.id], unit_type="user",
    )
    assert revisions["treatment"]["n"] == 3
    assert revisions["treatment"]["sum_value"] == 3  # (3-1)+(1-1)+(2-1)
    # Wrong unit type → zero-sample, never a bogus join
    empty = await _run_source(
        db, "projects", definition_key="project_approval_rate",
        units=[org.id], unit_type="organization",
    )
    assert empty["treatment"] == {"n": 0}


async def test_cost_ledger_source_org_and_tenant_units(db):
    from decimal import Decimal

    from app.models.evaluation import EvalType, EvaluationTask

    tenant, org = await _mk_org(db)
    for cost in (Decimal("0.25"), Decimal("0.50")):
        db.add(EvaluationTask(org_id=org.id, type=EvalType.EXERCISE_TEXT, cost_usd=cost))
    await db.flush()
    by_org = await _run_source(
        db, "cost_ledger", definition_key="cost_usd", units=[org.id],
        unit_type="organization",
    )
    assert by_org["treatment"]["n"] == 2
    assert by_org["treatment"]["sum_value"] == pytest.approx(0.75)
    by_tenant = await _run_source(
        db, "cost_ledger", definition_key="cost_usd", units=[tenant.id], unit_type="tenant",
    )
    assert by_tenant["treatment"]["sum_value"] == pytest.approx(0.75)
    # wrong unit type: exactly the zero-sample shape, never a bogus query
    wrong = await _run_source(
        db, "cost_ledger", definition_key="cost_usd", units=[org.id], unit_type="user",
    )
    assert wrong["treatment"] == {"n": 0}


async def test_registry_source_pack_adoption(db):
    from app.models.skill_pack import SkillPackInstallation

    _tenant, org = await _mk_org(db)
    user = await _mk_admin(db)
    db.add(SkillPackInstallation(org_id=org.id, installed_version="1.0.0", installed_by=user.id))
    db.add(SkillPackInstallation(org_id=org.id, installed_version="1.1.0", installed_by=user.id))
    await db.flush()
    result = await _run_source(
        db, "registry", definition_key="pack_adoption_rate", units=[org.id],
        unit_type="organization",
    )
    assert result["treatment"] == {"n": 1, "numerator": 2, "denominator": 1}


# Mutation-survivor ledger (metric sources): the per-source half-open window
# boundary pairs (>= window_start / < window_end in workflow_runs, projects,
# cost_ledger, client_briefs, registry, eco_telemetry) are template copies of
# the exposures-pinned contract (test_source_window_boundaries_half_open) —
# per-source boundary fixtures repeat the same predicate without adding
# information. promotion._validate_target's weights-sum tolerance boundary
# (abs(total-1.0) exactly == 1e-6) is not constructible in floats.


async def test_workflow_runs_source_all_measures(db):
    """success_rate, failure_rate and latency_ms (with cap) over real runs —
    the latency branch had no direct coverage."""

    from app.models.workflow_pack import WorkflowPackInstallation
    from app.models.workflow_run import RunStatus, WorkflowRun

    _tenant, org = await _mk_org(db)
    installation = WorkflowPackInstallation(org_id=org.id, installed_version="1.0.0")
    db.add(installation)
    await db.flush()
    window_start, _ = _today_window()
    t0 = window_start + timedelta(hours=1)
    # 3 completed / 1 failed: asymmetric so status==COMPLETED vs != is
    # distinguishable (2C+1F+1X collides: completed == not-completed == 2)
    runs = [
        (RunStatus.COMPLETED, t0, t0 + timedelta(milliseconds=100)),
        (RunStatus.COMPLETED, t0, t0 + timedelta(milliseconds=300)),
        (RunStatus.COMPLETED, t0, None),  # no finished_at → excluded from latency
        (RunStatus.FAILED, t0, t0 + timedelta(milliseconds=10_000)),
    ]
    for status, started, finished in runs:
        db.add(
            WorkflowRun(
                org_id=org.id, installation_id=installation.id,
                definition_snapshot={}, status=status,
                created_at=t0, started_at=started, finished_at=finished,
            )
        )
    await db.flush()
    units = [installation.id]
    success = await _run_source(
        db, "workflow_runs", definition_key="run_success_rate",
        units=units, unit_type="workflow_installation",
    )
    assert success["treatment"] == {"n": 4, "numerator": 3, "denominator": 4}
    failure = await _run_source(
        db, "workflow_runs", definition_key="run_failure_rate",
        units=units, unit_type="workflow_installation",
    )
    assert failure["treatment"] == {"n": 4, "numerator": 1, "denominator": 4}
    latency = await _run_source(
        db, "workflow_runs", definition_key="run_latency_ms",
        units=units, unit_type="workflow_installation",
    )
    # run_latency_ms seeds winsorize_pct=99.9: with three samples the
    # empirical 99.9th percentile IS the max → values unchanged, but the
    # adjustment ran and the source flags it for provenance (v2 §4.6)
    stats = latency["treatment"]
    assert stats["n"] == 3
    assert stats["sum_value"] == pytest.approx(100 + 300 + 10_000)
    assert stats["sum_sq"] == pytest.approx(100**2 + 300**2 + 10_000**2)
    assert stats["_winsorized"] is True


async def test_winsorize_helper_clamps_upper_tail():
    from app.experiments.services.metrics import winsorize

    values = [1.0, 2.0, 3.0, 4.0, 100.0]
    clamped, applied = winsorize(values, 80)  # 80th pct of 5 samples → 4.0
    assert applied is True
    assert clamped == [1.0, 2.0, 3.0, 4.0, 4.0]
    same, applied = winsorize(values, None)
    assert applied is False and same == values
    single, applied = winsorize([42.0], 99)
    assert applied is False  # <2 samples is a no-op


async def test_winsorized_provenance_is_truthful(db):
    """Provenance carries winsorize_pct ONLY on snapshots whose source
    actually applied it (the round-4 honesty rule, now with real application)."""
    from app.models.project import Project, Submission, SubmissionStatus

    await MetricService(db).ensure_seed_definitions()
    # Point revision_count at a winsorize pct for this test
    from app.experiments.models import MetricDefinition

    definition = (
        await db.execute(
            select(MetricDefinition).where(MetricDefinition.key == "revision_count")
        )
    ).scalar_one()
    definition.winsorize_pct = 99
    await db.flush()

    exp, admin = await _mk_running(db)
    # give the experiment a revision_count metric via a fresh spec? simpler:
    # compute directly through the source + compute_experiment_window with
    # the existing spec is exposure-only — assert at source level instead
    _tenant, org = await _mk_org(db)
    user = await _mk_admin(db)
    project = Project(
        org_id=org.id, title="P", slug=f"p-{str(ULID()).lower()}",
        description="d", instructions="i", rubric=[{"criterion": "c"}],
    )
    db.add(project)
    await db.flush()
    for version in (1, 2, 9):
        db.add(
            Submission(org_id=org.id, project_id=project.id, user_id=user.id,
                       status=SubmissionStatus.APPROVED, version=version)
        )
    await db.flush()
    out = await _run_source(
        db, "projects", definition_key="revision_count", units=[user.id], unit_type="user",
    )
    assert out["treatment"]["_winsorized"] is True


async def test_source_window_boundaries_half_open(db):
    """The shared window contract: occurred_at == window_start is IN,
    == window_end is OUT — pinned on the exposures source (every source
    copies the same >= start / < end predicate pair)."""
    from app.experiments.models import ExperimentAssignment, ExperimentExposure

    await MetricService(db).ensure_seed_definitions()
    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id="edge-1")
    await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id="edge-2")
    window_start, window_end = _today_window()
    rows = list(
        (
            await db.execute(
                select(ExperimentAssignment).where(
                    ExperimentAssignment.experiment_id == exp.id
                )
            )
        ).scalars()
    )
    db.add(
        ExperimentExposure(
            assignment_id=rows[0].id, experiment_id=exp.id, occurred_at=window_start
        )
    )
    db.add(
        ExperimentExposure(
            assignment_id=rows[1].id, experiment_id=exp.id, occurred_at=window_end
        )
    )
    await db.flush()
    from app.experiments.models import MetricDefinition
    from app.experiments.services.metrics import SOURCE_REGISTRY

    definition = (
        await db.execute(
            select(MetricDefinition).where(MetricDefinition.key == "exposure_rate")
        )
    ).scalar_one()
    variant_units: dict[str, list[str]] = {}
    for row in rows:
        variant_units.setdefault(row.variant_key, []).append(row.unit_id)
    out = await SOURCE_REGISTRY["exposures"](
        db, experiment=exp, definition=definition, variant_units=variant_units,
        window_start=window_start, window_end=window_end, unit_type="user",
    )
    # Only the window_start exposure counts; window_end belongs to the NEXT day
    total = sum(int(v.get("numerator") or 0) for v in out.values())
    assert total == 1


async def test_eco_telemetry_source_weighted_success(db):
    from app.ecosystem.models.graph import TelemetrySnapshot

    window_start, _ = _today_window()
    offering_id = str(ULID())
    db.add(
        TelemetrySnapshot(
            entity_kind="provider_offering", entity_id=offering_id,
            window_start=window_start, window_end=window_start + timedelta(hours=1),
            sample_size=100, metrics={"success_rate": 0.9},
        )
    )
    db.add(
        TelemetrySnapshot(
            entity_kind="provider_offering", entity_id=offering_id,
            window_start=window_start + timedelta(hours=1),
            window_end=window_start + timedelta(hours=2),
            sample_size=300, metrics={"success_rate": 0.5},
        )
    )
    # rows without a success_rate (or zero samples) are skipped, not crashed
    db.add(
        TelemetrySnapshot(
            entity_kind="provider_offering", entity_id=offering_id,
            window_start=window_start + timedelta(hours=2),
            window_end=window_start + timedelta(hours=3),
            sample_size=999, metrics={"latency_p50_ms": 12},
        )
    )
    await db.flush()
    result = await _run_source(
        db, "eco_telemetry", definition_key="provider_reliability",
        units=[offering_id], unit_type="provider_offering",
    )
    # weighted: (0.9·100 + 0.5·300) / 400 = 0.6
    stats = result["treatment"]
    assert stats["denominator"] == 400
    assert stats["numerator"] / stats["denominator"] == pytest.approx(0.6)


async def test_client_briefs_source_acceptance(db):
    from app.models.client_brief import BriefStatus, ClientBrief

    _tenant, org = await _mk_org(db)
    user = await _mk_admin(db)
    for status in (BriefStatus.COMPLETED, BriefStatus.REVIEW):
        db.add(
            ClientBrief(
                org_id=org.id, title="B", slug=f"b-{str(ULID()).lower()}",
                client_name="Client", project_type="image_set",
                objective="deliver assets", status=status, created_by=user.id,
            )
        )
    await db.flush()
    # asymmetric counts so status==completed vs != is distinguishable
    db.add(
        ClientBrief(
            org_id=org.id, title="B2", slug=f"b2-{str(ULID()).lower()}",
            client_name="Client", project_type="image_set",
            objective="deliver assets", status=BriefStatus.COMPLETED, created_by=user.id,
        )
    )
    await db.flush()
    result = await _run_source(
        db, "client_briefs", definition_key="client_acceptance_rate",
        units=[org.id], unit_type="organization",
    )
    assert result["treatment"]["denominator"] == 3
    assert result["treatment"]["numerator"] == 2


async def test_snapshot_unique_constraint_names_window(db):
    """The UPSERT targets uq_experiment_metric_snapshots_window — pin the
    constraint name so a rename breaks loudly here, not silently in prod."""
    names = {c.name for c in MetricSnapshot.__table__.constraints}
    assert "uq_experiment_metric_snapshots_window" in names


# ── CUPED covariates end-to-end (v2 batch 2, §4.6) ───────────────────


async def test_cuped_covariates_end_to_end(db):
    """Spec asks for CUPED on revision_count → the projects source switches
    to per-UNIT aggregation and emits pre-period covariate sufficient stats
    → the snapshot carries cov_* columns (provenance aggregation=per_unit)
    → analysis engages CUPED and the honesty warning disappears."""
    from app.experiments.models import ExperimentAssignment, MetricSnapshot
    from app.experiments.services.analysis_service import AnalysisService
    from app.models.project import Project, Submission, SubmissionStatus

    _tenant, org = await _mk_org(db)
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    spec = _spec()
    spec["metrics"]["primary"] = ["revision_count"]
    spec["variance_reduction"] = {
        "method": "cuped", "covariate_metric": "revision_count", "lookback_days": 28,
    }
    await svc.create_version(exp.id, spec=spec, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await MetricService(db).ensure_seed_definitions()

    project = Project(
        org_id=org.id, title="P", slug=f"p-{str(ULID()).lower()}",
        description="d", instructions="i", rubric=[{"criterion": "c", "max_score": 5}],
    )
    db.add(project)
    window_start, window_end = _today_window()
    # 8 users, 4 per arm; pre-period revisions (x) correlate with in-window
    # revisions (y): y = x + arm effect — CUPED has real variance to remove
    users: list[tuple[User, str, int]] = []
    for i in range(8):
        arm = "control" if i % 2 == 0 else "treatment"
        user = User(
            email=f"cuped-{ULID()}@example.com", display_name="U",
            role=UserRole.STUDENT, status=UserStatus.ACTIVE,
        )
        db.add(user)
        users.append((user, arm, i // 2))
    await db.flush()
    for user, arm, level in users:
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=user.id,
                variant_key=arm, assigned_version=1, bucket=0, is_holdout=False,
            )
        )
        # pre-period: `level` revisions at window_start - 7d
        db.add(
            Submission(
                org_id=org.id, project_id=project.id, user_id=user.id,
                status=SubmissionStatus.APPROVED, version=level + 1,
                created_at=window_start - timedelta(days=7),
            )
        )
        # in-window: y = level (+1 extra revision for treatment)
        y = level + (1 if arm == "treatment" else 0)
        db.add(
            Submission(
                org_id=org.id, project_id=project.id, user_id=user.id,
                status=SubmissionStatus.APPROVED, version=y + 1,
            )
        )
    await db.flush()

    written = await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    assert written >= 2
    snapshots = {
        row.variant_key: row
        for row in (
            await db.execute(
                select(MetricSnapshot).where(
                    MetricSnapshot.experiment_id == exp.id,
                    MetricSnapshot.metric_key == "revision_count",
                )
            )
        ).scalars()
    }
    control = snapshots["control"]
    # per-UNIT aggregation: n = units, not submissions
    assert control.n == 4
    assert control.provenance["aggregation"] == "per_unit"
    # x per control unit = (0,1,2,3); y identical in control
    assert float(control.cov_sum) == 6.0
    assert float(control.cov_sum_sq) == 14.0
    assert float(control.cov_xy_sum) == 14.0
    assert float(control.sum_value) == 6.0
    treatment = snapshots["treatment"]
    assert float(treatment.sum_value) == 10.0  # (1,2,3,4)
    assert float(treatment.cov_sum) == 6.0

    await svc.transition(exp.id, to_status="completed", actor=admin)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["revision_count"]["comparisons"]["treatment"]
    assert "cuped" in comparison
    assert "CUPED_COVARIATES_UNAVAILABLE" not in result["warnings"]


# ── Batch 3: newly wired sources (learning_paths / evaluations /
#    talent_outcomes / billing / capabilities) ────────────────────────


async def _mk_project(db, org):
    from app.models.project import Project

    project = Project(
        org_id=org.id, title="P", slug=f"p-{str(ULID()).lower()}",
        description="d", instructions="i", rubric=[{"criterion": "c", "max_score": 5}],
    )
    db.add(project)
    await db.flush()
    return project


async def test_learning_paths_source_completion_and_duration(db):
    """Completion = ALL required project items approved; completion time is
    the LAST approval; paths with required non-project items are excluded."""
    from app.models.learning_path import (
        ContentStatus,
        LearningPath,
        LearningPathItem,
        PathItemType,
    )
    from app.models.project import Submission, SubmissionStatus

    _tenant, org = await _mk_org(db)
    finisher = await _mk_admin(db)
    partial = await _mk_admin(db)
    p1 = await _mk_project(db, org)
    p2 = await _mk_project(db, org)
    path = LearningPath(
        org_id=org.id, name="Path", slug=f"lp-{str(ULID()).lower()}",
        status=ContentStatus.PUBLISHED,
    )
    db.add(path)
    await db.flush()
    db.add(LearningPathItem(
        path_id=path.id, item_type=PathItemType.PROJECT, project_id=p1.id,
        sort_order=0, required=True))
    db.add(LearningPathItem(
        path_id=path.id, item_type=PathItemType.PROJECT, project_id=p2.id,
        sort_order=1, required=True))
    # A path with a required non-project item is not derivable — completing
    # its project must NOT count
    p3 = await _mk_project(db, org)
    path2 = LearningPath(
        org_id=org.id, name="Mixed", slug=f"lp-{str(ULID()).lower()}",
        status=ContentStatus.PUBLISHED,
    )
    db.add(path2)
    await db.flush()
    db.add(LearningPathItem(
        path_id=path2.id, item_type=PathItemType.PROJECT, project_id=p3.id,
        sort_order=0, required=True))
    db.add(LearningPathItem(
        path_id=path2.id, item_type=PathItemType.SECTION, section_title="Theory",
        sort_order=1, required=True))

    window_start, window_end = _today_window()
    early = window_start - timedelta(days=2)
    # finisher: both required projects approved — first days ago, second now
    db.add(Submission(org_id=org.id, project_id=p1.id, user_id=finisher.id,
                      status=SubmissionStatus.APPROVED, version=1,
                      created_at=early, updated_at=early))
    db.add(Submission(org_id=org.id, project_id=p2.id, user_id=finisher.id,
                      status=SubmissionStatus.APPROVED, version=1,
                      created_at=early))  # updated_at defaults to now → in-window
    # partial: only one of two approved → NOT complete
    db.add(Submission(org_id=org.id, project_id=p1.id, user_id=partial.id,
                      status=SubmissionStatus.APPROVED, version=1))
    # partial completes the MIXED path's project — must not count
    db.add(Submission(org_id=org.id, project_id=p3.id, user_id=partial.id,
                      status=SubmissionStatus.APPROVED, version=1))
    await db.flush()

    completion = await _run_source(
        db, "learning_paths", definition_key="completion_rate",
        units=[finisher.id, partial.id], unit_type="user",
    )
    assert completion["treatment"] == {"n": 2, "numerator": 1, "denominator": 2}
    duration = await _run_source(
        db, "learning_paths", definition_key="time_to_completion_hours",
        units=[finisher.id, partial.id], unit_type="user",
    )
    assert duration["treatment"]["n"] == 1
    assert duration["treatment"]["sum_value"] >= 40  # ≥ ~2 days in hours
    # wrong unit type → zero-sample
    empty = await _run_source(
        db, "learning_paths", definition_key="completion_rate",
        units=[org.id], unit_type="organization",
    )
    assert empty["treatment"] == {"n": 0}


async def test_evaluations_source_review_pass_rate(db):
    from app.models.project import (
        ReviewerType,
        ReviewStatus,
        Submission,
        SubmissionReview,
        SubmissionStatus,
    )

    _tenant, org = await _mk_org(db)
    user = await _mk_admin(db)
    project = await _mk_project(db, org)
    sub = Submission(org_id=org.id, project_id=project.id, user_id=user.id,
                     status=SubmissionStatus.APPROVED, version=1)
    db.add(sub)
    await db.flush()
    db.add(SubmissionReview(submission_id=sub.id, reviewer_type=ReviewerType.AI,
                            status=ReviewStatus.APPROVED, score=90))
    db.add(SubmissionReview(submission_id=sub.id,
                            reviewer_type=ReviewerType.INSTRUCTOR,
                            status=ReviewStatus.REVISION_REQUESTED, score=40))
    # out-of-window review must not count
    old = datetime.now(UTC) - timedelta(days=3)
    db.add(SubmissionReview(submission_id=sub.id, reviewer_type=ReviewerType.AI,
                            status=ReviewStatus.APPROVED, score=95, created_at=old))
    await db.flush()
    stats = await _run_source(
        db, "evaluations", definition_key="practical_pass_rate",
        units=[user.id], unit_type="user",
    )
    assert stats["treatment"] == {"n": 2, "numerator": 1, "denominator": 2}


async def test_talent_outcomes_source_placements(db):
    from app.talent.models.application import Application, Placement
    from app.talent.models.employer import Opportunity

    _tenant, org = await _mk_org(db)
    placed = await _mk_admin(db)
    cancelled = await _mk_admin(db)
    silent = await _mk_admin(db)
    opp = Opportunity(employer_org_id=org.id, title="Role",
                      opportunity_type="contract", status="open")
    db.add(opp)
    await db.flush()

    async def _placement(user, status):
        application = Application(opportunity_id=opp.id, user_id=user.id,
                                  status="hired")
        db.add(application)
        await db.flush()
        db.add(Placement(application_id=application.id, opportunity_id=opp.id,
                         user_id=user.id, employer_org_id=org.id, status=status))

    await _placement(placed, "active")
    await _placement(cancelled, "cancelled")
    await db.flush()
    stats = await _run_source(
        db, "talent_outcomes", definition_key="placement_outcome_rate",
        units=[placed.id, cancelled.id, silent.id], unit_type="user",
    )
    assert stats["treatment"] == {"n": 3, "numerator": 1, "denominator": 3}


async def test_billing_source_tenant_measures(db):
    from app.controlplane.models.billing import Invoice, Subscription
    from app.controlplane.models.plan import PlanVersion, ProductPlan

    user = await _mk_admin(db)
    tenant_new, _org1 = await _mk_org(db)
    tenant_old, org2 = await _mk_org(db)
    tenant_churn, _org3 = await _mk_org(db)
    now = datetime.now(UTC)
    window_start, window_end = _today_window()
    plan = ProductPlan(key=f"exp-{str(ULID()).lower()[:8]}", name="Exp")
    db.add(plan)
    await db.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, status="active",
                     entitlements={}, activated_at=now)
    db.add(pv)
    await db.flush()

    def _invoice(tenant_id, total, paid_at):
        return Invoice(tenant_id=tenant_id, currency="USD", status="paid",
                       total_minor=total, paid_at=paid_at)

    # tenant_new: FIRST paid invoice lands in-window → converts
    db.add(_invoice(tenant_new.id, 5000, now))
    # tenant_old: paid before the window AND in it → no conversion, has ARPU
    db.add(_invoice(tenant_old.id, 10000, window_start - timedelta(days=30)))
    db.add(_invoice(tenant_old.id, 20000, now))

    def _sub(tenant_id, cancelled_at=None):
        return Subscription(
            tenant_id=tenant_id, plan_version_id=pv.id, status="active",
            currency="USD", interval="month", seat_quantity=0,
            current_period_start=window_start - timedelta(days=15),
            current_period_end=window_start + timedelta(days=15),
            provider="manual", created_by=user.id,
            created_at=window_start - timedelta(days=15),
            cancelled_at=cancelled_at,
        )

    db.add(_sub(tenant_old.id))
    db.add(_sub(tenant_churn.id, cancelled_at=window_start + timedelta(hours=2)))
    await db.flush()
    units = [tenant_new.id, tenant_old.id, tenant_churn.id]

    conversion = await _run_source(
        db, "billing", definition_key="conversion_rate", units=units, unit_type="tenant",
    )
    assert conversion["treatment"] == {"n": 3, "numerator": 1, "denominator": 3}

    arpu = await _run_source(
        db, "billing", definition_key="arpu_usd", units=units, unit_type="tenant",
    )
    # 50.00 + 200.00 + 0.00 (ITT zero for silent tenant)
    assert arpu["treatment"]["n"] == 3
    assert arpu["treatment"]["sum_value"] == 250.0

    retention = await _run_source(
        db, "billing", definition_key="retention_rate", units=units, unit_type="tenant",
    )
    # at risk: tenant_old (retained) + tenant_churn (cancelled mid-window);
    # tenant_new had no subscription at window start
    assert retention["treatment"] == {"n": 2, "numerator": 1, "denominator": 2}

    margin = await _run_source(
        db, "billing", definition_key="gross_margin_pct", units=units, unit_type="tenant",
    )
    # both revenue tenants, no eval cost → 100% margin each
    assert margin["treatment"]["n"] == 2
    assert margin["treatment"]["sum_value"] == 200.0
    del org2  # revenue tenants only — org fixture unused beyond creation

    # org units refused (would double-count tenant revenue)
    empty = await _run_source(
        db, "billing", definition_key="arpu_usd", units=[_org1.id],
        unit_type="organization",
    )
    assert empty["treatment"] == {"n": 0}


async def test_capabilities_source_gain_needs_baseline(db):
    from app.talent.models.capability import Capability
    from app.talent.models.scoring import CapabilityScoreSnapshot

    _tenant, _org = await _mk_org(db)
    grower = await _mk_admin(db)
    newcomer = await _mk_admin(db)
    cap = Capability(canonical_name=f"Cap {ULID()}", slug=f"cap-{str(ULID()).lower()}",
                     category="technical")
    db.add(cap)
    await db.flush()
    window_start, _window_end = _today_window()

    def _snap(user, score, computed_at):
        return CapabilityScoreSnapshot(
            user_id=user.id, capability_id=cap.id, score=score, depth=score,
            breadth=score, recency=score, velocity=score, confidence=score,
            level=1, evidence_count=1, scoring_version="v1",
            computed_at=computed_at,
        )

    # grower: baseline 0.40 → in-window 0.65 = gain 0.25
    db.add(_snap(grower, 0.40, window_start - timedelta(days=10)))
    db.add(_snap(grower, 0.65, window_start + timedelta(hours=1)))
    # newcomer: first-ever score in-window — enrollment, not gain
    db.add(_snap(newcomer, 0.90, window_start + timedelta(hours=1)))
    await db.flush()
    stats = await _run_source(
        db, "capabilities", definition_key="capability_gain",
        units=[grower.id, newcomer.id], unit_type="user",
    )
    assert stats["treatment"]["n"] == 1
    assert abs(stats["treatment"]["sum_value"] - 0.25) < 1e-9
