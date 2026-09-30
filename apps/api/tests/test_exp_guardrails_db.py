"""Guardrail/SRM DB tests (ADR-017 exp04).

Breach → auto-pause via the locked state machine; SRM is alert-only; manual
incident pauses; sweep fairness (oldest-checked first, stamp after
processing); unwired guardrail sources skip; and the structural guarantee
that no auto-promote path exists in the experiments package.

Runs against the dev Postgres (exp04 applied); rollback-per-test.
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.experiments.models import (
    INCIDENT_GUARDRAIL_KEY,
    SRM_GUARDRAIL_KEY,
    Experiment,
    ExperimentAssignment,
    ExperimentEvent,
)
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.guardrails import GuardrailService
from app.experiments.services.layers import LayerService
from app.experiments.services.metrics import MetricService
from app.experiments.worker import (
    handle_evaluate_guardrails,
    sweep_experiment_guardrails,
)
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def _spec(guardrails: list[dict] | None = None) -> dict:
    return {
        "hypothesis": "guardrails pause unsafe experiments automatically",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {
            "primary": ["exposure_rate"],
            "guardrails": guardrails
            if guardrails is not None
            else [{"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}],
        },
    }


async def _mk_admin(db) -> User:
    user = User(
        email=f"exp-guard-{ULID()}@example.com",
        display_name="G",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_running(db, *, guardrails: list[dict] | None = None):
    await MetricService(db).ensure_seed_definitions()
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
    await svc.create_version(exp.id, spec=_spec(guardrails), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    return exp, admin


# ── Breach → auto-pause ──────────────────────────────────────────────


async def test_breach_pauses_and_records_event(db):
    # exposure_rate must stay <= 0.4; expose 100% of assigned units → breach
    exp, _ = await _mk_running(
        db,
        guardrails=[
            {"metric_key": "exposure_rate", "op": "lte", "threshold": 0.4, "window_hours": 24}
        ],
    )
    asvc = AssignmentService(db)
    for i in range(10):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"g-{i}")
        assert r is not None
        await asvc.record_exposure(experiment_key=exp.key, unit_type="user", unit_id=f"g-{i}")
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"] and summary["breaches"][0]["metric_key"] == "exposure_rate"
    assert (await db.get(Experiment, exp.id)).status == "paused"
    events = await GuardrailService(db).list_events(exp.id)
    assert any(e.action == "paused" and e.auto for e in events)
    audit = list(
        (
            await db.execute(
                select(ExperimentEvent).where(
                    ExperimentEvent.experiment_id == exp.id,
                    ExperimentEvent.event_type == "guardrail_paused",
                )
            )
        ).scalars()
    )
    assert audit, "guardrail pause must land in the append-only audit trail"


async def test_no_breach_no_pause_but_stamped(db):
    exp, _ = await _mk_running(
        db,
        guardrails=[
            {"metric_key": "exposure_rate", "op": "lte", "threshold": 0.9, "window_hours": 24}
        ],
    )
    asvc = AssignmentService(db)
    for i in range(10):
        await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"n-{i}")
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"] == []
    exp_row = await db.get(Experiment, exp.id)
    assert exp_row.status == "running"
    assert exp_row.last_guardrail_check_at is not None


async def test_unwired_guardrail_source_skips_not_pauses(db):
    exp, _ = await _mk_running(
        db, guardrails=[{"metric_key": "cost_usd", "op": "lte", "threshold": 0.0001}]
    )
    await AssignmentService(db).resolve(
        experiment_key=exp.key, unit_type="user", unit_id="u" * 26
    )
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"] == []
    assert (await db.get(Experiment, exp.id)).status == "running"


async def test_gte_guardrail_direction(db):
    # exposure_rate must stay >= 0.5; nobody exposed → observed 0 → breach
    exp, _ = await _mk_running(
        db,
        guardrails=[
            {"metric_key": "exposure_rate", "op": "gte", "threshold": 0.5, "window_hours": 24}
        ],
    )
    asvc = AssignmentService(db)
    for i in range(10):
        await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"gte-{i}")
    await GuardrailService(db).evaluate_experiment(exp.id)
    assert (await db.get(Experiment, exp.id)).status == "paused"


async def test_paused_experiment_is_skipped(db):
    exp, admin = await _mk_running(db)
    await ExperimentService(db).transition(exp.id, to_status="paused", actor=admin)
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary.get("skipped") is True


# ── SRM (alert-only) ─────────────────────────────────────────────────


async def test_srm_alerts_but_never_pauses(db):
    exp, _ = await _mk_running(db)
    # Manufacture a gross 150/10 skew on a 50/50 design (bypasses resolve)
    for i in range(150):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"srm-a-{i:04d}",
                variant_key="control", assigned_version=1, bucket=i % 10_000,
            )
        )
    for i in range(10):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"srm-b-{i:04d}",
                variant_key="treatment", assigned_version=1, bucket=i % 10_000,
            )
        )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "srm" in summary
    assert (await db.get(Experiment, exp.id)).status == "running", "SRM must never pause"
    events = await GuardrailService(db).list_events(exp.id)
    srm_events = [e for e in events if e.guardrail_key == SRM_GUARDRAIL_KEY]
    assert len(srm_events) == 1 and srm_events[0].action == "alerted"
    # Re-evaluation within the suppression window must not duplicate the alert
    await GuardrailService(db).evaluate_experiment(exp.id)
    events = await GuardrailService(db).list_events(exp.id)
    assert len([e for e in events if e.guardrail_key == SRM_GUARDRAIL_KEY]) == 1


async def test_srm_quiet_below_min_sample(db):
    exp, _ = await _mk_running(db)
    for i in range(30):  # heavy skew but under SRM_MIN_ASSIGNMENTS
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"small-{i:03d}",
                variant_key="control", assigned_version=1, bucket=i,
            )
        )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "srm" not in summary


async def test_unparseable_spec_pauses_instead_of_dead_lettering(db):
    """Poison-spec resilience: if a stored spec stops parsing (schema drift,
    bad data repair), guardrails CANNOT run — the experiment must be paused
    with __spec_invalid__, never left silently unguarded while the handler
    dead-letters forever."""
    from sqlalchemy import update as _update

    from app.experiments.models import ExperimentVersion

    exp, _ = await _mk_running(db)
    await db.execute(
        _update(ExperimentVersion)
        .where(ExperimentVersion.experiment_id == exp.id)
        .values(spec={"totally": "corrupt"})
    )
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"][0]["metric_key"] == "__spec_invalid__"
    exp_row = await db.get(Experiment, exp.id)
    assert exp_row.status == "paused"
    assert exp_row.last_guardrail_check_at is not None
    events = await GuardrailService(db).list_events(exp.id)
    assert any(e.guardrail_key == "__spec_invalid__" and e.action == "paused" for e in events)


async def test_closure_sweep_survives_poison_spec(db):
    """One unparseable spec must not stall the closure batch for everyone."""
    from sqlalchemy import update as _update

    from app.experiments.models import ExperimentVersion
    from app.experiments.worker import sweep_experiment_closures

    poison, _ = await _mk_running(db)
    healthy, _ = await _mk_running(db)
    now = datetime.now(UTC)
    (await db.get(Experiment, poison.id)).started_at = now - timedelta(days=40)
    (await db.get(Experiment, healthy.id)).started_at = now - timedelta(days=40)
    await db.execute(
        _update(ExperimentVersion)
        .where(ExperimentVersion.experiment_id == poison.id)
        .values(spec={"totally": "corrupt"})
    )
    await db.flush()
    closed = await sweep_experiment_closures(db)
    assert closed >= 1
    assert (await db.get(Experiment, healthy.id)).status == "completed"
    assert (await db.get(Experiment, poison.id)).status == "running"  # skipped, logged


def test_terminal_statuses_match_live_key_partial_index():
    """Parity guard: the live-key partial index WHERE clause and
    security.TERMINAL_STATUSES must name the same set — a new terminal
    status added to one but not the other silently breaks key reuse or
    uniqueness."""
    from app.experiments.models.experiment import Experiment as ExpModel
    from app.experiments.security import TERMINAL_STATUSES

    index = next(
        idx for idx in ExpModel.__table__.indexes if idx.name == "uq_experiments_live_key"
    )
    where_sql = str(index.dialect_options["postgresql"]["where"])
    for status in TERMINAL_STATUSES:
        assert f"'{status}'" in where_sql, f"{status} missing from live-key index WHERE"
    import re

    quoted = set(re.findall(r"'([a-z_]+)'", where_sql))
    assert quoted == set(TERMINAL_STATUSES)


# ── Manual incident ──────────────────────────────────────────────────


async def test_incident_pauses_immediately(db):
    exp, admin = await _mk_running(db)
    event = await GuardrailService(db).record_incident(
        exp.id, actor=admin, reason="privacy report"
    )
    assert event.guardrail_key == INCIDENT_GUARDRAIL_KEY
    assert event.auto is False
    assert (await db.get(Experiment, exp.id)).status == "paused"


# ── Sweep fairness ───────────────────────────────────────────────────


async def test_sweep_oldest_checked_first_with_cap(db):
    # §106.25 law: the shared dev DB accumulates committed RUNNING
    # experiments from other suites; stamp them checked-now so this test's
    # ancient/never-checked trio deterministically leads the capped batch.
    from sqlalchemy import update

    await db.execute(
        update(Experiment)
        .where(Experiment.status == "running")
        .values(last_guardrail_check_at=datetime.now(UTC))
    )
    exp_a, _ = await _mk_running(db)
    exp_b, _ = await _mk_running(db)
    exp_c, _ = await _mk_running(db)
    now = datetime.now(UTC)
    # a checked long ago, b recently, c never
    (await db.get(Experiment, exp_a.id)).last_guardrail_check_at = now - timedelta(hours=5)
    (await db.get(Experiment, exp_b.id)).last_guardrail_check_at = now - timedelta(minutes=1)
    await db.flush()
    from app.controlplane.models.outbox import OutboxMessage

    await sweep_experiment_guardrails(db, cap=2)
    rows = list(
        (
            await db.execute(
                select(OutboxMessage).where(
                    OutboxMessage.topic == "exp.evaluate_guardrails",
                    OutboxMessage.status == "pending",
                )
            )
        ).scalars()
    )
    mine = {m.payload["experiment_id"] for m in rows} & {exp_a.id, exp_b.id, exp_c.id}
    # never-checked (c) and oldest-checked (a) win the capped batch
    assert mine == {exp_c.id, exp_a.id}


async def test_handler_evaluates_and_stamps(db):
    exp, _ = await _mk_running(db)
    await handle_evaluate_guardrails(db, {"experiment_id": exp.id})
    assert (await db.get(Experiment, exp.id)).last_guardrail_check_at is not None


# ── Structural: no auto-promote path (§2.2) ──────────────────────────


def test_no_auto_promote_path_in_experiments_package():
    """Grep-level guarantee: nothing under app/experiments/ transitions to
    'promoted' automatically. The SINGLE allowed site is
    services/decisions.py (exp06): an explicit human decision — its create()
    requires an actor (approver), status `analyzed`, and a verified
    analysis_result_hash. Everything else (guardrails, worker, sweeps,
    assignment, promotion apply) must never promote."""
    pkg = Path(__file__).resolve().parents[1] / "app" / "experiments"
    offenders = []
    decision_sites = 0
    for path in pkg.rglob("*.py"):
        if path.name in ("security.py",):  # vocabulary constants live here
            continue
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            code = line.split("#", 1)[0]
            if 'to_status="promoted"' in code or "to_status='promoted'" in code:
                if path.name == "decisions.py":
                    decision_sites += 1
                else:
                    offenders.append(f"{path.name}:{lineno}")
    assert not offenders, f"auto-promote path found: {offenders}"
    # The human-decision site exists exactly once and is approver-gated
    assert decision_sites == 1
    decisions_src = (pkg / "services" / "decisions.py").read_text(encoding="utf-8")
    assert "actor: User" in decisions_src
    assert "DECISION_HASH_MISMATCH" in decisions_src  # no decide-before-analyze
    # Round 3: the LITERAL scan alone was insufficient — the generic
    # transition endpoint passes USER-SUPPLIED to_status, so the service must
    # refuse promoted/rejected outside the decision path, and the bypass
    # token (_via_decision=True) may only be spent by decisions.py.
    experiments_src = (pkg / "services" / "experiments.py").read_text(encoding="utf-8")
    assert "EXPERIMENT_DECISION_REQUIRED" in experiments_src
    spenders = [
        path.name
        for path in pkg.rglob("*.py")
        if "_via_decision=True" in path.read_text(encoding="utf-8")
        and path.name != "decisions.py"
    ]
    assert not spenders, f"_via_decision spent outside decisions.py: {spenders}"
