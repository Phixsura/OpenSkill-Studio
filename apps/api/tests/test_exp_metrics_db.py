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
            "secondary": ["completion_rate"],  # learning_paths source unwired (exp09)
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
    # exposure_rate + cost_usd guardrail (zero-sample for user units) per
    # variant; the unwired learning_paths secondary is skipped
    assert written == 4
    snapshots = await MetricService(db).list_snapshots(exp.id)
    assert {s.metric_key for s in snapshots} == {"exposure_rate", "cost_usd"}
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
    """completion_rate's learning_paths source lands in exp09 (derived
    progress) — computing today must skip it (logged) and still write the
    wired metrics."""
    assert "learning_paths" not in SOURCE_REGISTRY
    await MetricService(db).ensure_seed_definitions()
    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    for i in range(20):  # enough units to land in both variants
        await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"skip-{i}")
    window_start, window_end = _today_window()
    written = await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_end
    )
    assert written == 4  # exposure_rate + cost_usd guardrail × 2 variants


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
    result = await _run_source(
        db, "client_briefs", definition_key="client_acceptance_rate",
        units=[org.id], unit_type="organization",
    )
    assert result["treatment"]["denominator"] == 2
    assert result["treatment"]["numerator"] == 1


async def test_snapshot_unique_constraint_names_window(db):
    """The UPSERT targets uq_experiment_metric_snapshots_window — pin the
    constraint name so a rename breaks loudly here, not silently in prod."""
    names = {c.name for c in MetricSnapshot.__table__.constraints}
    assert "uq_experiment_metric_snapshots_window" in names
