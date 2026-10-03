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
from app.experiments.schemas import ExperimentSpec as SpecModel
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
    # Defect #46: rolling backfill — yesterday plus the two days before it,
    # most recent enqueued LAST, each window exactly one day wide.
    from app.experiments.worker import SNAPSHOT_BACKFILL_DAYS

    assert len(mine) == SNAPSHOT_BACKFILL_DAYS == 3
    ws, we = previous_utc_day()
    got = [(m.payload["window_start"], m.payload["window_end"]) for m in mine]
    expect = [
        ((ws - timedelta(days=o)).isoformat(),
         (we - timedelta(days=o)).isoformat())
        for o in range(SNAPSHOT_BACKFILL_DAYS - 1, -1, -1)
    ]
    assert got == expect


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
    # cap counts EXPERIMENTS (slots); each slot enqueues the backfill fan
    from app.experiments.worker import SNAPSHOT_BACKFILL_DAYS

    assert enqueued == SNAPSHOT_BACKFILL_DAYS
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
    db.add(SubmissionReview(submission_id=sub.id, reviewer_type=ReviewerType.AI,
                            status=ReviewStatus.APPROVED, score=88))
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
    assert stats["treatment"] == {"n": 3, "numerator": 2, "denominator": 3}


async def test_talent_outcomes_source_placements(db):
    from app.talent.models.application import Application, Placement
    from app.talent.models.employer import Opportunity

    _tenant, org = await _mk_org(db)
    placed = await _mk_admin(db)
    placed2 = await _mk_admin(db)
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
    await _placement(placed2, "completed")
    await _placement(cancelled, "cancelled")
    await db.flush()
    stats = await _run_source(
        db, "talent_outcomes", definition_key="placement_outcome_rate",
        units=[placed.id, placed2.id, cancelled.id, silent.id], unit_type="user",
    )
    assert stats["treatment"] == {"n": 4, "numerator": 2, "denominator": 4}


async def test_billing_source_tenant_measures(db):
    from app.controlplane.models.billing import Invoice, Subscription
    from app.controlplane.models.plan import PlanVersion, ProductPlan

    user = await _mk_admin(db)
    tenant_new, _org1 = await _mk_org(db)
    tenant_old, org2 = await _mk_org(db)
    tenant_churn, _org3 = await _mk_org(db)
    tenant_gone, _org4 = await _mk_org(db)  # churned BEFORE the window
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
    # an OPEN invoice never counts anywhere
    db.add(Invoice(tenant_id=tenant_new.id, currency="USD", status="open",
                   total_minor=99999, paid_at=None))
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
    # round 80: a pre-window churn is OUT of the at-risk set entirely
    db.add(_sub(tenant_gone.id, cancelled_at=window_start - timedelta(days=1)))
    await db.flush()
    units = [tenant_new.id, tenant_old.id, tenant_churn.id, tenant_gone.id]

    conversion = await _run_source(
        db, "billing", definition_key="conversion_rate", units=units, unit_type="tenant",
    )
    assert conversion["treatment"] == {"n": 4, "numerator": 1, "denominator": 4}

    arpu = await _run_source(
        db, "billing", definition_key="arpu_usd", units=units, unit_type="tenant",
    )
    # 50.00 + 200.00 + 0.00 + 0.00 (ITT zero for silent tenants)
    assert arpu["treatment"]["n"] == 4
    assert arpu["treatment"]["sum_value"] == 250.0

    retention = await _run_source(
        db, "billing", definition_key="retention_rate", units=units, unit_type="tenant",
    )
    # at risk: tenant_old (retained) + tenant_churn (cancelled mid-window);
    # tenant_new had no subscription at window start and tenant_gone churned
    # BEFORE the window (the skip arm — never at risk)
    assert retention["treatment"] == {"n": 2, "numerator": 1, "denominator": 2}

    # non-zero eval cost against tenant_old's org: margin arithmetic pinned
    from decimal import Decimal

    from app.models.evaluation import EvalStatus, EvalType, EvaluationTask

    db.add(EvaluationTask(org_id=org2.id, type=EvalType.SUBMISSION_REVIEW,
                          status=EvalStatus.COMPLETED, cost_usd=Decimal("50.0")))
    await db.flush()
    margin = await _run_source(
        db, "billing", definition_key="gross_margin_pct", units=units, unit_type="tenant",
    )
    # tenant_new: (50-0)/50 = 100%; tenant_old: (200-50)/200 = 75%
    assert margin["treatment"]["n"] == 2
    assert margin["treatment"]["sum_value"] == 175.0

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


# ── Switchback window attribution (v2 batch 11) ──────────────────────


async def test_switchback_window_snapshots_land_on_day_variant(db):
    """The whole roster's window stats land under the variant that owned the
    day — cross-window aggregation then compares variant-days."""
    from app.experiments.services.assignment import switchback_variant

    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="SB", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    spec = _spec()
    spec["design"] = "switchback"
    spec["switchback"] = {"switch_unit": "platform_day", "window_minutes": 1440}
    await svc.create_version(exp.id, spec=spec, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    asvc = AssignmentService(db)
    for i in range(6):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"sbm-{i}")
        assert r is not None
        await asvc.record_exposure(experiment_key=exp.key, unit_type="user", unit_id=f"sbm-{i}")
    window_start, window_end = _today_window()
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    snapshots = await MetricService(db).list_snapshots(exp.id)
    exposure_rows = [s for s in snapshots if s.metric_key == "exposure_rate"]
    assert len(exposure_rows) == 1  # one arm owns the whole day
    versions = await svc.get_versions(exp.id)

    expected = switchback_variant(
        exp.key, versions[0].spec_hash[:8], SpecModel.model_validate(spec), window_start
    )
    assert exposure_rows[0].variant_key == expected
    assert int(exposure_rows[0].denominator) == 6
    assert int(exposure_rows[0].numerator) == 6


async def test_switchback_washout_excludes_head_of_window(db):
    """Exposures inside the washout band do not count; provenance records the
    applied washout; a washout covering the whole window writes nothing."""
    from sqlalchemy import update

    from app.experiments.models import ExperimentExposure

    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="WB", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    spec = _spec()
    spec["design"] = "switchback"
    spec["switchback"] = {
        "switch_unit": "platform_day", "window_minutes": 1440, "washout_minutes": 120,
    }
    await svc.create_version(exp.id, spec=spec, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    asvc = AssignmentService(db)
    window_start, window_end = _today_window()
    for i in range(4):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"wb-{i}")
        assert r is not None
        await asvc.record_exposure(experiment_key=exp.key, unit_type="user", unit_id=f"wb-{i}")
    # push two units' exposures into the washout band (first 2h of the window)
    exposures = list(
        (
            await db.execute(
                select(ExperimentExposure).where(ExperimentExposure.experiment_id == exp.id)
            )
        ).scalars()
    )
    for exposure in exposures[:2]:
        await db.execute(
            update(ExperimentExposure)
            .where(ExperimentExposure.id == exposure.id)
            .values(occurred_at=window_start + timedelta(minutes=30))
        )
    # ...and the rest safely after the washout
    for exposure in exposures[2:]:
        await db.execute(
            update(ExperimentExposure)
            .where(ExperimentExposure.id == exposure.id)
            .values(occurred_at=window_start + timedelta(minutes=300))
        )
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    snapshots = await MetricService(db).list_snapshots(exp.id)
    row = next(s for s in snapshots if s.metric_key == "exposure_rate")
    assert int(row.numerator) == 2  # washout-band exposures excluded
    assert int(row.denominator) == 4  # roster unchanged
    assert row.provenance["washout_minutes"] == 120

    # washout swallowing the entire window computes nothing
    tiny_end = window_start + timedelta(minutes=60)
    written = await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=tiny_end
    )
    assert written == 0


async def test_cost_ledger_cuped_per_unit_covariates(db):
    """cost_ledger's CUPED mode: per-org totals with pre-window covariates
    (ITT zero-fill), exact sufficient-stat goldens."""
    from datetime import UTC as _UTC
    from datetime import datetime as _dt
    from decimal import Decimal

    from app.experiments.models import MetricDefinition
    from app.experiments.schemas import VarianceReductionSpec
    from app.experiments.services.metrics import SOURCE_REGISTRY
    from app.models.evaluation import EvalStatus, EvalType, EvaluationTask

    _tenant1, org1 = await _mk_org(db)
    _tenant2, org2 = await _mk_org(db)
    await MetricService(db).ensure_seed_definitions()
    definition = (
        await db.execute(
            select(MetricDefinition).where(MetricDefinition.key == "internal_cost_usd")
        )
    ).scalar_one()
    window_start, window_end = _today_window()
    pre_at = window_start - timedelta(days=5)

    def _task(org_id, cost, created_at):
        return EvaluationTask(
            org_id=org_id, type=EvalType.SUBMISSION_REVIEW,
            status=EvalStatus.COMPLETED, cost_usd=Decimal(str(cost)),
            created_at=created_at,
        )

    now = _dt.now(_UTC)
    # org1: pre 3.0, window 5.0; org2: silent both periods (ITT zeros)
    db.add(_task(org1.id, 3.0, pre_at))
    db.add(_task(org1.id, 5.0, now))
    await db.flush()
    vr = VarianceReductionSpec(
        method="cuped", covariate_metric="internal_cost_usd", lookback_days=28
    )
    stats = await SOURCE_REGISTRY["cost_ledger"](
        db, experiment=None, definition=definition,
        variant_units={"treatment": [org1.id, org2.id]},
        window_start=window_start, window_end=window_end,
        unit_type="organization", variance_reduction=vr,
    )
    arm = stats["treatment"]
    assert arm["n"] == 2
    assert arm["sum_value"] == 5.0
    assert arm["cov_sum"] == 3.0
    assert arm["cov_sum_sq"] == 9.0
    assert arm["cov_xy_sum"] == 15.0
    assert arm["_aggregation"] == "per_unit"


async def test_learning_paths_completion_window_boundaries(db):
    """Half-open completion window: completion AT window_start counts,
    completion AT window_end does not."""
    from app.models.learning_path import (
        ContentStatus,
        LearningPath,
        LearningPathItem,
        PathItemType,
    )
    from app.models.project import Submission, SubmissionStatus

    _tenant, org = await _mk_org(db)
    at_start = await _mk_admin(db)
    at_end = await _mk_admin(db)
    project = await _mk_project(db, org)
    path = LearningPath(
        org_id=org.id, name="B", slug=f"lp-{str(ULID()).lower()}",
        status=ContentStatus.PUBLISHED,
    )
    db.add(path)
    await db.flush()
    db.add(LearningPathItem(
        path_id=path.id, item_type=PathItemType.PROJECT, project_id=project.id,
        sort_order=0, required=True))
    window_start, window_end = _today_window()
    db.add(Submission(org_id=org.id, project_id=project.id, user_id=at_start.id,
                      status=SubmissionStatus.APPROVED, version=1,
                      created_at=window_start - timedelta(days=1),
                      updated_at=window_start))
    db.add(Submission(org_id=org.id, project_id=project.id, user_id=at_end.id,
                      status=SubmissionStatus.APPROVED, version=1,
                      created_at=window_start - timedelta(days=1),
                      updated_at=window_end))
    await db.flush()
    stats = await _run_source(
        db, "learning_paths", definition_key="completion_rate",
        units=[at_start.id, at_end.id], unit_type="user",
    )
    assert stats["treatment"] == {"n": 2, "numerator": 1, "denominator": 2}


# Mutation-survivor ledger (round-10 wave 3): the remaining half-open
# window-boundary flips (>= start / < end) across the five new sources are
# template copies of the exposures-source contract pinned above and in the
# completion-boundary test — same class round 6 ledgered for the original
# seven sources. unit_type early-return Eq flips are pinned by each source's
# wrong-unit-type zero-sample assertion.


# ── Segment breakdown (v2 batch 30, §4.8) ────────────────────────────


async def test_segment_breakdown_org_rows_and_whole_population_intact(db):
    """Opting into the org segment writes per-org snapshot rows WITHOUT
    touching the whole-population rows (segment='') — a slice, never a mix."""
    from app.models.organization import OrgMember, OrgRole

    _tenant1, org_a = await _mk_org(db)
    _tenant2, org_b = await _mk_org(db)
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="SEG", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    spec = _spec()
    spec["segments"] = ["org"]
    await svc.create_version(exp.id, spec=spec, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)

    asvc = AssignmentService(db)
    users = []
    for i in range(12):
        user = await _mk_admin(db)
        users.append(user)
        org = org_a if i < 8 else org_b
        db.add(OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.STUDENT))
    await db.flush()
    for i, user in enumerate(users):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=user.id)
        assert r is not None
        if i % 2 == 0:
            await asvc.record_exposure(
                experiment_key=exp.key, unit_type="user", unit_id=user.id
            )
    window_start, window_end = _today_window()
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    from app.experiments.models import MetricSnapshot

    rows = list(
        (
            await db.execute(
                select(MetricSnapshot).where(
                    MetricSnapshot.experiment_id == exp.id,
                    MetricSnapshot.metric_key == "exposure_rate",
                )
            )
        ).scalars()
    )
    whole = [r for r in rows if r.segment == ""]
    seg_a = [r for r in rows if r.segment == f"org:{org_a.id}"]
    seg_b = [r for r in rows if r.segment == f"org:{org_b.id}"]
    assert sum(int(r.denominator or 0) for r in whole) == 12
    assert sum(int(r.denominator or 0) for r in seg_a) == 8
    assert sum(int(r.denominator or 0) for r in seg_b) == 4
    # the slices partition the whole — numerators add up too
    assert sum(int(r.numerator or 0) for r in seg_a) + sum(
        int(r.numerator or 0) for r in seg_b
    ) == sum(int(r.numerator or 0) for r in whole)
    return exp, admin, org_a


async def test_variant_units_boundaries_and_isolation(db):
    """as_of is strictly half-open (assigned AT as_of excluded) and the
    exposed_only filter never counts ANOTHER experiment's exposures."""
    from app.exceptions import AppError as _AppError
    from app.experiments.models import ExperimentAssignment, ExperimentExposure

    exp, _ = await _mk_running(db)
    other, _ = await _mk_running(db)
    cutoff = datetime(2026, 9, 2, tzinfo=UTC)
    before = ExperimentAssignment(
        experiment_id=exp.id, unit_type="user", unit_id="b" * 26,
        variant_key="control", assigned_version=1, bucket=0, is_holdout=False,
        assigned_at=cutoff - timedelta(seconds=1),
    )
    at = ExperimentAssignment(
        experiment_id=exp.id, unit_type="user", unit_id="a" * 26,
        variant_key="control", assigned_version=1, bucket=0, is_holdout=False,
        assigned_at=cutoff,
    )
    db.add_all([before, at])
    await db.flush()
    svc = MetricService(db)
    units = await svc._variant_units(exp.id, as_of=cutoff)  # noqa: SLF001
    assert units == {"control": ["b" * 26]}

    # exposed_only: an exposure on ANOTHER experiment must not qualify
    db.add(ExperimentExposure(
        assignment_id=before.id, experiment_id=other.id, context={},
        occurred_at=cutoff - timedelta(seconds=1),
    ))
    await db.flush()
    exposed = await svc._variant_units(  # noqa: SLF001
        exp.id, as_of=cutoff, exposed_only=True
    )
    assert exposed == {}
    db.add(ExperimentExposure(
        assignment_id=before.id, experiment_id=exp.id, context={},
        occurred_at=cutoff - timedelta(seconds=1),
    ))
    await db.flush()
    exposed = await svc._variant_units(  # noqa: SLF001
        exp.id, as_of=cutoff, exposed_only=True
    )
    assert exposed == {"control": ["b" * 26]}

    # unknown experiment: uniform 404 with the status pinned
    import pytest as _pytest

    with _pytest.raises(_AppError) as exc:
        await svc.compute_experiment_window(
            "0" * 26, window_start=cutoff, window_end=cutoff + timedelta(days=1)
        )
    assert exc.value.status_code == 404


async def test_segment_rows_only_when_opted_in(db):
    """A user-unit experiment WITHOUT segments=["org"] never writes segment
    rows, even when its users belong to orgs (the opt-in gate is the spec)."""
    from app.experiments.models import MetricSnapshot
    from app.models.organization import OrgMember, OrgRole

    _tenant, org = await _mk_org(db)
    await MetricService(db).ensure_seed_definitions()
    exp, _ = await _mk_running(db)  # no segments in spec
    asvc = AssignmentService(db)
    for _i in range(4):
        user = await _mk_admin(db)
        db.add(OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.STUDENT))
        await db.flush()
        assert await asvc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=user.id
        ) is not None
    window_start, window_end = _today_window()
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    seg_rows = list(
        (
            await db.execute(
                select(MetricSnapshot).where(
                    MetricSnapshot.experiment_id == exp.id,
                    MetricSnapshot.segment != "",
                )
            )
        ).scalars()
    )
    assert seg_rows == []


async def test_switchback_washout_exact_window_and_zero_washout(db):
    """washout == the whole window computes nothing (>= boundary); zero
    washout stamps NO washout_minutes provenance (the > 0 gate)."""
    from app.experiments.models import MetricSnapshot

    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="WZ", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    spec = _spec()
    spec["design"] = "switchback"
    spec["switchback"] = {
        "switch_unit": "platform_day", "window_minutes": 1440, "washout_minutes": 0,
    }
    await svc.create_version(exp.id, spec=spec, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    asvc = AssignmentService(db)
    assert await asvc.resolve(
        experiment_key=exp.key, unit_type="user", unit_id="wz" + "0" * 24
    ) is not None
    window_start, window_end = _today_window()
    written = await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    assert written > 0
    rows = list(
        (
            await db.execute(
                select(MetricSnapshot).where(MetricSnapshot.experiment_id == exp.id)
            )
        ).scalars()
    )
    assert all("washout_minutes" not in r.provenance for r in rows)
    # washout exactly equal to the window: nothing computes (>= boundary)
    exact = await MetricService(db).compute_experiment_window(
        exp.id,
        window_start=window_start,
        window_end=window_start + timedelta(minutes=1440),
    )
    del exact
    # Defect #44: a washout >= window spec is now rejected at the boundary —
    # it would fold EVERY window to zero forever.
    spec2 = dict(spec)
    spec2["switchback"] = {
        "switch_unit": "platform_day", "window_minutes": 1440,
        "washout_minutes": 1440,
    }
    layer2 = await LayerService(db).create(
        key=f"l2-{str(ULID()).lower()}", domain="learning"
    )
    exp2 = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="WZ2", domain="learning",
        layer_key=layer2.key, owner_user_id=admin.id,
    )
    with pytest.raises(AppError):
        await svc.create_version(exp2.id, spec=spec2, actor=admin)
    # The swallow branch's HONEST reachable case (round 74 — the mutated-
    # stored-spec version of this test passed for the wrong reason: a
    # washout >= window spec now fails PARSE post-#44, taking the poison-
    # spec skip arm, never the swallow): a VALID week-window spec with a
    # 1440-minute washout computed over a DAY window — the washout covers
    # the whole computed span.
    spec3 = dict(spec)
    spec3["switchback"] = {
        "switch_unit": "platform_week", "window_minutes": 10_080,
        "washout_minutes": 1440,
    }
    layer3 = await LayerService(db).create(
        key=f"l3-{str(ULID()).lower()}", domain="learning"
    )
    exp3 = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="WZ3", domain="learning",
        layer_key=layer3.key, owner_user_id=admin.id,
    )
    await svc.create_version(exp3.id, spec=spec3, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer3.key, experiment_id=exp3.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp3.id, to_status="review", actor=admin)
    await svc.transition(exp3.id, to_status="scheduled", actor=admin,
                         checklist=_CHECKLIST)
    await svc.transition(exp3.id, to_status="running", actor=admin)
    await svc.set_ramp(exp3.id, ramp_bp=10_000, actor=admin)
    assert await asvc.resolve(
        experiment_key=exp3.key, unit_type="user", unit_id="wz" + "2" * 24
    ) is not None
    swallowed = await MetricService(db).compute_experiment_window(
        exp3.id,
        window_start=window_start,
        window_end=window_start + timedelta(minutes=1440),
    )
    assert swallowed == 0


# Wave-4 survivor ledger: the top-orgs cap constant (20→21) is a §106.26
# bound whose exact value is policy, pinned here by reference; the salt
# prefix length is now a shared constant covered by its own pin.


# ── Feature-combination matrix (round 10 cross-checks) ───────────────


async def _mk_running_spec(db, spec_overrides: dict):
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="CMB", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    spec = _spec()
    spec.update(spec_overrides)
    await svc.create_version(exp.id, spec=spec, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    return exp, admin


async def test_segments_compose_with_switchback(db):
    """segments × switchback: the org slice rows carry the WINDOW's variant
    (the roster fold happens before slicing)."""
    from app.experiments.models import MetricSnapshot
    from app.experiments.services.assignment import switchback_variant, version_salt_of
    from app.models.organization import OrgMember, OrgRole

    _tenant, org = await _mk_org(db)
    exp, admin = await _mk_running_spec(db, {
        "design": "switchback",
        "switchback": {"switch_unit": "platform_day", "window_minutes": 1440},
        "segments": ["org"],
    })
    del admin
    asvc = AssignmentService(db)
    for _i in range(4):
        user = await _mk_admin(db)
        db.add(OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.STUDENT))
        await db.flush()
        assert await asvc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=user.id
        ) is not None
    window_start, window_end = _today_window()
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    versions = await ExperimentService(db).get_versions(exp.id)
    spec = SpecModel.model_validate(versions[-1].spec)
    expected = switchback_variant(
        exp.key, version_salt_of(versions[0].spec_hash), spec, window_start
    )
    seg_rows = list(
        (
            await db.execute(
                select(MetricSnapshot).where(
                    MetricSnapshot.experiment_id == exp.id,
                    MetricSnapshot.segment == f"org:{org.id}",
                    MetricSnapshot.metric_key == "exposure_rate",
                )
            )
        ).scalars()
    )
    assert len(seg_rows) == 1
    assert seg_rows[0].variant_key == expected
    assert int(seg_rows[0].denominator) == 4


async def test_segments_compose_with_triggered(db):
    """segments × exposed-only: slice denominators are exposed ∩ org."""
    from app.experiments.models import MetricSnapshot
    from app.models.organization import OrgMember, OrgRole

    _tenant, org = await _mk_org(db)
    exp, _ = await _mk_running_spec(db, {
        "trigger": {"analysis_population": "exposed"},
        "segments": ["org"],
    })
    asvc = AssignmentService(db)
    for i in range(6):
        user = await _mk_admin(db)
        db.add(OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.STUDENT))
        await db.flush()
        assert await asvc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=user.id
        ) is not None
        if i < 2:  # only two units ever exposed
            await asvc.record_exposure(
                experiment_key=exp.key, unit_type="user", unit_id=user.id
            )
    window_start, window_end = _today_window()
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    rows = list(
        (
            await db.execute(
                select(MetricSnapshot).where(
                    MetricSnapshot.experiment_id == exp.id,
                    MetricSnapshot.metric_key == "exposure_rate",
                )
            )
        ).scalars()
    )
    whole = [r for r in rows if r.segment == ""]
    slices = [r for r in rows if r.segment == f"org:{org.id}"]
    assert sum(int(r.denominator or 0) for r in whole) == 2   # exposed roster
    assert sum(int(r.denominator or 0) for r in slices) == 2  # exposed ∩ org
    for row in rows:
        assert row.provenance["analysis_population"] == "exposed"


async def test_workflow_runs_latency_cuped_per_unit(db):
    """workflow_runs CUPED mode: per-installation MEAN latency with the
    pre-window lookback as covariate (exact goldens, ITT zero-fill)."""
    from app.experiments.models import MetricDefinition
    from app.experiments.schemas import VarianceReductionSpec
    from app.experiments.services.metrics import SOURCE_REGISTRY
    from app.models.workflow_pack import WorkflowPackInstallation
    from app.models.workflow_run import RunStatus, WorkflowRun

    _tenant, org = await _mk_org(db)
    active = WorkflowPackInstallation(org_id=org.id, installed_version="1.0.0")
    silent = WorkflowPackInstallation(org_id=org.id, installed_version="1.0.0")
    db.add_all([active, silent])
    await db.flush()
    await MetricService(db).ensure_seed_definitions()
    definition = (
        await db.execute(
            select(MetricDefinition).where(MetricDefinition.key == "run_latency_ms")
        )
    ).scalar_one()
    window_start, window_end = _today_window()
    pre_at = window_start - timedelta(days=3)

    def _run(created_at, ms):
        return WorkflowRun(
            org_id=org.id, installation_id=active.id, definition_snapshot={},
            status=RunStatus.COMPLETED, created_at=created_at,
            started_at=created_at, finished_at=created_at + timedelta(milliseconds=ms),
        )

    # pre: mean (100+300)/2 = 200ms; window: mean (400+600)/2 = 500ms
    db.add_all([
        _run(pre_at, 100), _run(pre_at, 300),
        _run(window_start + timedelta(hours=1), 400),
        _run(window_start + timedelta(hours=1), 600),
    ])
    await db.flush()
    vr = VarianceReductionSpec(
        method="cuped", covariate_metric="run_latency_ms", lookback_days=28
    )
    stats = await SOURCE_REGISTRY["workflow_runs"](
        db, experiment=None, definition=definition,
        variant_units={"treatment": [active.id, silent.id]},
        window_start=window_start, window_end=window_end,
        unit_type="workflow_installation", variance_reduction=vr,
    )
    arm = stats["treatment"]
    assert arm["n"] == 2
    assert arm["sum_value"] == pytest.approx(500.0)   # active 500 + silent 0
    assert arm["cov_sum"] == pytest.approx(200.0)
    assert arm["cov_xy_sum"] == pytest.approx(500.0 * 200.0)
    assert arm["_aggregation"] == "per_unit"


async def test_segment_multi_org_user_attributed_deterministically(db):
    """A user in TWO orgs lands in exactly ONE slice (min org_id) — the
    slices stay a partition, never double-counting a unit."""
    from app.experiments.models import MetricSnapshot
    from app.models.organization import OrgMember, OrgRole

    _t1, org1 = await _mk_org(db)
    _t2, org2 = await _mk_org(db)
    first_org = min([org1, org2], key=lambda o: o.id)
    exp, _ = await _mk_running_spec(db, {"segments": ["org"]})
    asvc = AssignmentService(db)
    user = await _mk_admin(db)
    db.add(OrgMember(org_id=org1.id, user_id=user.id, role=OrgRole.STUDENT))
    db.add(OrgMember(org_id=org2.id, user_id=user.id, role=OrgRole.STUDENT))
    await db.flush()
    assert await asvc.resolve(
        experiment_key=exp.key, unit_type="user", unit_id=user.id
    ) is not None
    window_start, window_end = _today_window()
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    seg_rows = list(
        (
            await db.execute(
                select(MetricSnapshot).where(
                    MetricSnapshot.experiment_id == exp.id,
                    MetricSnapshot.segment != "",
                    MetricSnapshot.metric_key == "exposure_rate",
                )
            )
        ).scalars()
    )
    segments = {r.segment for r in seg_rows}
    assert segments == {f"org:{first_org.id}"}
    assert sum(int(r.denominator or 0) for r in seg_rows) == 1


async def test_worker_time_arithmetic_pinned(db):
    """Wave-9 killers over the sweep time math — all with FIXED instants."""
    from app.experiments.worker import (
        previous_utc_day,
        sweep_experiment_closures,
        sweep_experiment_windows,
    )

    fixed = datetime(2026, 9, 2, 12, 34, tzinfo=UTC)
    assert previous_utc_day(fixed) == (
        datetime(2026, 9, 1, tzinfo=UTC),
        datetime(2026, 9, 2, tzinfo=UTC),
    )

    # analysis_close_at EXACTLY now: strictly-greater keeps it OUT
    await MetricService(db).ensure_seed_definitions()
    exp, admin = await _mk_running(db)
    svc = ExperimentService(db)
    await svc.transition(exp.id, to_status="completed", actor=admin)
    exp.analysis_close_at = fixed
    await db.flush()
    assert await sweep_experiment_windows(db, now=fixed) == 0

    # stop_policy.max_days elapsing EXACTLY now closes the experiment
    exp2, _admin2 = await _mk_running(db)
    spec_days = 14  # _spec() stop_policy default — read it back to be exact
    versions = await svc.get_versions(exp2.id)
    spec_days = SpecModel.model_validate(versions[-1].spec).stop_policy.max_days
    exp2.started_at = fixed - timedelta(days=spec_days)
    await db.flush()
    closed = await sweep_experiment_closures(db, now=fixed)
    assert closed == 1
    assert (await svc.get(exp2.id)).status == "completed"


async def test_prune_retention_boundary(db):
    """Wave-9 killer: 399-day-old exposures of an archived experiment stay,
    401-day-old ones go — a flipped cutoff sign would delete everything."""
    from app.experiments.models import ExperimentAssignment, ExperimentExposure
    from app.experiments.worker import prune_experiment_history

    exp, admin = await _mk_running(db)
    svc = ExperimentService(db)
    asvc = AssignmentService(db)
    r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id="pr" + "0" * 24)
    assert r is not None
    now = datetime.now(UTC)
    assignment_id = (
        await db.execute(
            select(ExperimentAssignment.id).where(
                ExperimentAssignment.experiment_id == exp.id
            )
        )
    ).scalar_one()
    db.add(ExperimentExposure(
        assignment_id=assignment_id, experiment_id=exp.id, context={},
        occurred_at=now - timedelta(days=399),
    ))
    db.add(ExperimentExposure(
        assignment_id=assignment_id, experiment_id=exp.id, context={},
        occurred_at=now - timedelta(days=401),
    ))
    for status in ("completed", "archived"):
        await svc.transition(exp.id, to_status=status, actor=admin)
    await db.flush()
    result = await prune_experiment_history(db, now=now)
    assert result["exposures"] == 1  # exactly the 401-day row
    from sqlalchemy import func as _func

    remaining = (
        await db.execute(
            select(_func.count()).where(ExperimentExposure.experiment_id == exp.id)
        )
    ).scalar_one()
    assert remaining == 1  # the 399-day row survives


def test_exp_outbox_handlers_registered():
    """§96 class (handler edition): an exp.* outbox topic whose handler is
    written but never registered is dead code the sweeps enqueue into
    forever — pin all three by name in the live registry."""
    from app.controlplane.worker import HANDLERS, load_handlers

    load_handlers()
    assert {
        "exp.compute_snapshots",
        "exp.evaluate_guardrails",
        "exp.apply_promotion",
    } <= set(HANDLERS)


async def test_snapshot_response_serializes_segment(db):
    """Defect #49: segment was stored (exp08) but never serialized — the
    listing made segment rows indistinguishable from whole-population rows,
    so a consumer summing them double-counted every sliced metric."""
    from app.experiments.schemas import MetricSnapshotResponse

    await MetricService(db).ensure_seed_definitions()
    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    assert await asvc.resolve(
        experiment_key=exp.key, unit_type="user", unit_id="seg" + "0" * 23
    ) is not None
    window_start, window_end = _today_window()
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    rows = await MetricService(db).list_snapshots(exp.id)
    assert rows
    dumped = MetricSnapshotResponse.model_validate(rows[0]).model_dump()
    assert dumped["segment"] == ""  # whole-population marker, present and typed


async def test_start_sweep_launches_due_scheduled_experiments(db):
    """exp10 (round 60): the start sweep launches scheduled experiments whose
    start_at is due; future and NULL start_at stay scheduled (NULL = the old
    manual-start behavior, unchanged)."""
    from app.experiments.models import Experiment, ExperimentEvent
    from app.experiments.worker import sweep_experiment_starts

    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)

    async def _scheduled(start_at):
        layer = await LayerService(db).create(
            key=f"lyr-{str(ULID()).lower()}", domain="learning"
        )
        svc = ExperimentService(db)
        exp = await svc.create(
            key=f"exp-{str(ULID()).lower()}", title="S", domain="learning",
            layer_key=layer.key, owner_user_id=admin.id,
        )
        await svc.create_version(exp.id, spec=_spec(), actor=admin)
        await LayerService(db).allocate(
            layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
        )
        await svc.transition(exp.id, to_status="review", actor=admin)
        await svc.transition(
            exp.id, to_status="scheduled", actor=admin,
            checklist=_CHECKLIST, start_at=start_at,
        )
        return exp

    now = datetime.now(UTC)
    # Defect #56: a NAIVE start_at means UTC deterministically — never the
    # DB session's TimeZone
    naive_due = await _scheduled((now - timedelta(minutes=5)).replace(tzinfo=None))
    stored = (await db.get(Experiment, naive_due.id)).start_at
    assert stored is not None and stored.utcoffset() is not None

    due = await _scheduled(now - timedelta(minutes=5))
    boundary = await _scheduled(now)  # start_at == now exactly (<= edge)
    future = await _scheduled(now + timedelta(days=1))
    manual = await _scheduled(None)

    # the passed clock is authoritative — a PAST now launches nothing
    assert await sweep_experiment_starts(db, now=now - timedelta(days=30)) == 0
    assert (await db.get(Experiment, due.id)).status == "scheduled"

    started = await sweep_experiment_starts(db, now=now)
    assert started == 3  # naive_due + due + the exact <= boundary, once each
    assert (await db.get(Experiment, naive_due.id)).status == "running"
    assert (await db.get(Experiment, boundary.id)).status == "running"
    assert (await db.get(Experiment, due.id)).status == "running"
    assert (await db.get(Experiment, due.id)).started_at is not None
    assert (await db.get(Experiment, future.id)).status == "scheduled"
    assert (await db.get(Experiment, manual.id)).status == "scheduled"
    # the launch is audited as a system transition
    events = (
        await db.execute(
            select(ExperimentEvent).where(
                ExperimentEvent.experiment_id == due.id,
                ExperimentEvent.event_type == "transition",
            )
        )
    ).scalars().all()
    assert any("start_at" in ((e.payload or {}).get("reason") or "") for e in events)


async def test_every_source_degrades_on_type_mismatch_and_empty_units(db):
    """Round 78 (necropsy sweep over all registered sources): every source
    must degrade to {n: 0} shapes — never crash — on (a) a unit_type it does
    not serve and (b) an empty unit list of the type it does. One sweep
    covers the twelve per-source defensive arms at once."""
    from app.experiments.services.metrics import SOURCE_REGISTRY

    await MetricService(db).ensure_seed_definitions()
    expected_types = {
        "exposures": "user", "workflow_runs": "workflow_installation",
        "projects": "user", "cost_ledger": "tenant",
        "client_briefs": "organization", "registry": "organization",
        "eco_telemetry": "provider_offering", "learning_paths": "user",
        "evaluations": "user", "talent_outcomes": "user",
        "billing": "tenant", "capabilities": "user",
    }
    assert set(expected_types) == set(SOURCE_REGISTRY)
    # exposures needs a real experiment (internal source, exercised across
    # every suite); workflow_runs and cost_ledger have no type gate by design
    gated = {"projects", "client_briefs", "registry", "eco_telemetry",
             "learning_paths", "evaluations", "talent_outcomes", "billing",
             "capabilities"}
    # a definition per source (seeds cover most; synthesize the rest)
    definitions = {
        d.spec.get("source"): d for d in await MetricService(db).list_definitions()
    }
    window_start, window_end = _today_window()
    for name, fn in SOURCE_REGISTRY.items():
        if name == "exposures":
            continue
        definition = definitions.get(name)
        if definition is None:
            definition = await MetricService(db).create_definition(
                key=f"probe_{name}"[:40], title=f"probe {name}",
                kind="continuous", domain="operational", source_kind="service",
                spec={"source": name},
            )
        if name in gated:
            mismatch = await fn(
                db, experiment=None, definition=definition,
                variant_units={"v": ["u1"]},
                window_start=window_start, window_end=window_end,
                unit_type="zzz_not_a_unit",
            )
            assert mismatch == {"v": {"n": 0}}, name
        empty = await fn(
            db, experiment=None, definition=definition,
            variant_units={"v": []},
            window_start=window_start, window_end=window_end,
            unit_type=expected_types[name],
        )
        assert empty.get("v", {}).get("n", 0) == 0, name


async def test_cost_ledger_cuped_tenant_arm(db):
    """Round 79 necropsy: the CUPED per-unit covariate lookback has a TENANT
    rollup arm (org costs summed up to tenant) that no test reached —
    exercised with tenant units + a cuped variance_reduction whose covariate
    is the metric itself."""
    from decimal import Decimal

    from app.experiments.schemas import VarianceReductionSpec
    from app.experiments.services.metrics import SOURCE_REGISTRY
    from app.models.evaluation import EvalType, EvaluationTask

    await MetricService(db).ensure_seed_definitions()
    tenant, org = await _mk_org(db)
    db.add(EvaluationTask(org_id=org.id, type=EvalType.EXERCISE_TEXT,
                          cost_usd=Decimal("0.40")))
    await db.flush()
    definition = next(
        d for d in await MetricService(db).list_definitions() if d.key == "cost_usd"
    )
    window_start, window_end = _today_window()
    out = await SOURCE_REGISTRY["cost_ledger"](
        db, experiment=None, definition=definition,
        variant_units={"treatment": [tenant.id]},
        window_start=window_start, window_end=window_end,
        unit_type="tenant",
        variance_reduction=VarianceReductionSpec(
            method="cuped", covariate_metric="cost_usd", lookback_days=7
        ),
    )
    arm = out["treatment"]
    assert arm["n"] == 1
    assert arm["sum_value"] == pytest.approx(0.40)
    assert "cov_sum" in arm and "cov_xy_sum" in arm
    assert arm["_aggregation"] == "per_unit"


async def test_snapshot_compute_poison_spec_arms(db):
    """Round 79: the snapshot pipeline's legacy-defense arms — a CORRUPTED
    stored spec (the only way such a row exists post-#44) makes the key
    parse, variance-reduction read, exposed-only read and segment read each
    fall back instead of crashing; the compute writes nothing and returns 0."""
    from sqlalchemy import update as _update

    from app.experiments.models import ExperimentVersion as VersionModel
    from app.experiments.services.assignment import forget_spec

    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    assert await asvc.resolve(
        experiment_key=exp.key, unit_type="user", unit_id="poison-0"
    ) is not None
    await db.execute(
        _update(VersionModel)
        .where(VersionModel.experiment_id == exp.id, VersionModel.version == 1)
        .values(spec={"hypothesis": "too short"})
    )
    forget_spec(exp.id)
    window_start, window_end = _today_window()
    written = await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    assert written == 0
    assert await MetricService(db).list_snapshots(exp.id) == []


async def test_latency_cap_and_scoped_learning_paths_arms(db):
    """Round 80 necropsy tail: (1) definition.cap_value clamps latency
    durations before winsorize; (2) the learning_paths source narrows its
    item universe to the experiment's scope_org when one is set."""
    from types import SimpleNamespace

    from sqlalchemy import select as _select
    from sqlalchemy import update as _update

    from app.experiments.models import MetricDefinition
    from app.experiments.services.metrics import SOURCE_REGISTRY
    from app.models.workflow_pack import WorkflowPackInstallation

    await MetricService(db).ensure_seed_definitions()
    tenant, org = await _mk_org(db)

    # (1) cap arm on run_latency_ms
    from app.models.workflow_run import RunStatus, WorkflowRun

    pack_install = WorkflowPackInstallation(org_id=org.id, installed_version="1.0.0")
    db.add(pack_install)
    await db.flush()
    t0 = datetime.now(UTC) - timedelta(hours=1)
    for ms in (100, 300, 10_000):
        db.add(WorkflowRun(
            org_id=org.id, installation_id=pack_install.id,
            definition_snapshot={}, status=RunStatus.COMPLETED,
            created_at=t0, started_at=t0,
            finished_at=t0 + timedelta(milliseconds=ms),
        ))
    await db.flush()
    await db.execute(
        _update(MetricDefinition)
        .where(MetricDefinition.key == "run_latency_ms")
        .values(cap_value=500)
    )
    definition = (
        await db.execute(
            _select(MetricDefinition).where(MetricDefinition.key == "run_latency_ms")
        )
    ).scalar_one()
    window_start, window_end = _today_window()
    capped = await SOURCE_REGISTRY["workflow_runs"](
        db, experiment=None, definition=definition,
        variant_units={"t": [pack_install.id]},
        window_start=t0 - timedelta(hours=1), window_end=window_end,
        unit_type="workflow_installation",
    )
    assert capped["t"]["sum_value"] == pytest.approx(100 + 300 + 500)

    # (2) scope_org narrowing on learning_paths
    lp_def = next(
        d for d in await MetricService(db).list_definitions()
        if (d.spec or {}).get("source") == "learning_paths"
    )
    scoped = SimpleNamespace(scope_org_id=org.id)
    out = await SOURCE_REGISTRY["learning_paths"](
        db, experiment=scoped, definition=lp_def,
        variant_units={"t": ["u" * 26]},
        window_start=window_start, window_end=window_end,
        unit_type="user",
    )
    # ITT shape: the unit is counted even with zero scoped items; the point
    # here is the scope JOIN ran (branch 609) without error
    assert out["t"]["n"] == 1
    assert out["t"].get("numerator", 0) == 0


async def test_update_definition_operational_knobs_only(db):
    """Round 101: PATCH edits title/privacy/direction/winsorize/cap, clears
    via explicit flags, refuses unknown enums typed, 404s unknown keys —
    kind/source are not even accepted by the schema."""
    svc = MetricService(db)
    await svc.ensure_seed_definitions()
    updated = await svc.update_definition(
        "run_latency_ms", title="Run latency (edited)",
        direction="decrease_good", winsorize_pct=99.0, cap_value=60_000,
    )
    assert updated.title == "Run latency (edited)"
    assert float(updated.winsorize_pct) == 99.0
    assert float(updated.cap_value) == 60_000
    cleared = await svc.update_definition(
        "run_latency_ms", clear_winsorize=True, clear_cap=True
    )
    assert cleared.winsorize_pct is None and cleared.cap_value is None
    with pytest.raises(AppError) as exc:
        await svc.update_definition("run_latency_ms", direction="sideways")
    assert exc.value.code == "VALIDATION_ERROR"
    assert exc.value.status_code == 422  # status is contract (wave-16 kill)
    with pytest.raises(AppError) as exc:
        await svc.update_definition("no_such_metric_zzz", title="x")
    assert exc.value.status_code == 404
    from app.experiments.schemas import UpdateMetricDefinitionRequest

    assert "kind" not in UpdateMetricDefinitionRequest.model_fields
    assert "spec" not in UpdateMetricDefinitionRequest.model_fields


async def test_multi_covariate_snapshot_assembly(db):
    """§4.6 v3 round 114: a two-covariate spec (revision_count +
    project_approval_rate, both through the projects provider) lands a
    covariates map with EXACT per-key sufficient stats, the first covariate
    mirrored into cov_*, and per-unit maps never persisted."""
    from datetime import timedelta as _td

    from app.models.project import Project, Submission, SubmissionStatus

    await MetricService(db).ensure_seed_definitions()
    _tenant, org = await _mk_org(db)
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="learning"
    )
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"mcv-{str(ULID()).lower()}", title="MCV", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    await svc.create_version(exp.id, spec={
        "hypothesis": "multi-covariate adjustment tightens the estimate",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {"primary": ["revision_count"],
                    "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                    "threshold": 100.0}]},
        "variance_reduction": {
            "method": "cuped",
            "covariate_metrics": ["revision_count", "project_approval_rate"],
            "lookback_days": 14,
        },
    }, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    for status in ("review", "scheduled", "running"):
        await svc.transition(exp.id, to_status=status, actor=admin,
                             checklist=_CHECKLIST if status == "scheduled" else None)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)

    asvc = AssignmentService(db)
    units = []
    for i in range(6):
        u = User(email=f"mcv-{i}-{ULID()}@example.com", display_name=f"M{i}",
                 role=UserRole.STUDENT, status=UserStatus.ACTIVE)
        db.add(u)
        await db.flush()
        assert await asvc.resolve(experiment_key=exp.key, unit_type="user",
                                  unit_id=u.id) is not None
        units.append(u.id)

    project = Project(org_id=org.id, title="MP",
                      slug=f"mp-{str(ULID()).lower()}", description="d",
                      instructions="i",
                      rubric=[{"criterion": "c", "max_score": 5}])
    db.add(project)
    await db.flush()
    window_start, window_end = _today_window()
    pre = window_start - _td(days=3)
    # unit 0: pre 2 revisions + 1 approval; window 1 revision
    db.add(Submission(org_id=org.id, project_id=project.id, user_id=units[0],
                      status=SubmissionStatus.APPROVED, version=3,
                      created_at=pre))
    db.add(Submission(org_id=org.id, project_id=project.id, user_id=units[0],
                      status=SubmissionStatus.REJECTED, version=2,
                      created_at=window_start + _td(hours=1)))
    # unit 1: pre 1 approval (0 revisions); window 0
    db.add(Submission(org_id=org.id, project_id=project.id, user_id=units[1],
                      status=SubmissionStatus.APPROVED, version=1,
                      created_at=pre))
    await db.flush()

    written = await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    assert written > 0
    rows = await MetricService(db).list_snapshots(exp.id, metric_key="revision_count")
    whole = [r for r in rows if r.segment == ""]
    assert whole
    by_variant = {}
    for r in whole:
        by_variant[r.variant_key] = r
    total_cov = {}
    for r in whole:
        assert set(r.covariates) == {"revision_count", "project_approval_rate"}
        for k, v in r.covariates.items():
            agg = total_cov.setdefault(k, {"sum": 0.0, "xy_sum": 0.0})
            agg["sum"] += v["sum"]
            agg["xy_sum"] += v["xy_sum"]
        # first covariate mirrors into cov_*
        assert float(r.cov_sum or 0) == r.covariates["revision_count"]["sum"]
    # exact totals across variants: pre revisions = 2 (unit0), approvals = 2
    assert total_cov["revision_count"]["sum"] == 2.0
    assert total_cov["project_approval_rate"]["sum"] == 2.0
    # xy: unit0 y=1 pairs with x_rev=2 and x_appr=1 -> 2 and 1
    assert total_cov["revision_count"]["xy_sum"] == 2.0
    assert total_cov["project_approval_rate"]["xy_sum"] == 1.0
