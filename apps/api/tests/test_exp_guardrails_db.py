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
    GuardrailEvent,
)
from app.experiments.security import ETHICS_CHECKLIST_KEY, LAUNCH_CHECKLIST_KEYS
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

_CHECKLIST = {key: True for key in (*LAUNCH_CHECKLIST_KEYS, ETHICS_CHECKLIST_KEY)}

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
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
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
    """Round 77 rewrite — the original passed for the wrong reason: cost_usd
    gained a wired source in exp07, so neither defensive arm ran. The honest
    arms: (1) a guardrail naming a metric with NO definition, (2) one whose
    definition's source isn't in the registry — both skip with a warning,
    neither pauses, neither crashes."""
    from ulid import ULID as _ULID

    from app.experiments.services.metrics import MetricService as MetricSvc

    probe_key = f"unwired_{str(_ULID()).lower()[:10]}"
    await MetricSvc(db).ensure_seed_definitions()
    await MetricSvc(db).create_definition(
        key=probe_key, title="Unwired probe", kind="continuous",
        domain="operational", source_kind="service",
        spec={"source": "no_such_source"},
    )
    exp, _ = await _mk_running(
        db, guardrails=[
            {"metric_key": "ghost_metric_zzz", "op": "lte", "threshold": 1.0},
            {"metric_key": probe_key, "op": "lte", "threshold": 1.0},
        ]
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
    # Pin the χ² arithmetic exactly: expected 80/80 on a 50/50 spec,
    # chi2 = (150-80)²/80 + (10-80)²/80 = 122.5, df = 1, total = 160
    srm = summary["srm"]
    assert srm["total"] == 160
    assert srm["counts"] == {"control": 150, "treatment": 10}
    assert srm["df"] == 1
    assert srm["chi2"] == pytest.approx(122.5, abs=1e-6)
    assert (await db.get(Experiment, exp.id)).status == "running", "SRM must never pause"
    events = await GuardrailService(db).list_events(exp.id)
    srm_events = [e for e in events if e.guardrail_key == SRM_GUARDRAIL_KEY]
    assert len(srm_events) == 1 and srm_events[0].action == "alerted"
    # Re-evaluation within the suppression window must not duplicate the alert
    await GuardrailService(db).evaluate_experiment(exp.id)
    events = await GuardrailService(db).list_events(exp.id)
    assert len([e for e in events if e.guardrail_key == SRM_GUARDRAIL_KEY]) == 1


async def test_srm_fires_exactly_at_min_sample_boundary(db):
    """total == SRM_MIN_ASSIGNMENTS must be checked (the < boundary): 100
    units all in one arm of a 50/50 spec is a maximal mismatch."""
    from app.experiments.services.guardrails import SRM_MIN_ASSIGNMENTS

    exp, _ = await _mk_running(db)
    for i in range(SRM_MIN_ASSIGNMENTS):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"bnd-{i:04d}",
                variant_key="control", assigned_version=1, bucket=i % 10_000,
            )
        )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "srm" in summary
    assert summary["srm"]["total"] == SRM_MIN_ASSIGNMENTS


async def test_srm_runs_at_max_variant_count(db):
    """df = 9 (ten variants — the spec maximum) must still be evaluated: the
    df-range guard is exclusive of impossible values only."""
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    variants = [
        {"key": f"v{i}", "name": f"V{i}", "weight_bp": 1000, "is_control": i == 0}
        for i in range(10)
    ]
    await svc.create_version(
        exp.id,
        spec={
            "hypothesis": "ten-way test exercises the df=9 SRM path fully",
            "unit_type": "user",
            "variants": variants,
            "metrics": {
                "primary": ["exposure_rate"],
                "guardrails": [{"metric_key": "cost_usd", "op": "lte", "threshold": 1.0}],
            },
        },
        actor=admin,
    )
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    for status in ("review", "scheduled", "running"):
        await svc.transition(
            exp.id, to_status=status, actor=admin,
            checklist=_CHECKLIST if status == "scheduled" else None,
        )
    # 120 units all in v0: gross mismatch across 10 arms (df = 9)
    for i in range(120):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"ten-{i:04d}",
                variant_key="v0", assigned_version=1, bucket=i % 10_000,
            )
        )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "srm" in summary
    assert summary["srm"]["df"] == 9


# Mutation-survivor ledger (service-core sweep): the following mutants are
# equivalent/unreachable/display-level and intentionally not killed —
#   assignment.py pick_variant final return (weights sum to 10000 ⇒ the loop
#     always returns; the fallback line is unreachable by construction);
#   check_srm df<1 (specs require ≥2 variants) and expected==0 (zero weights
#     are spec-rejected) guards are unreachable;
#   df>9 vs >10 differs only at 11+ variants (spec max is 10);
#   chi2 exactly equal to the critical value is not constructible in floats;
#   the re-alert window's >= boundary needs microsecond-exact created_at;
#   limit(1)→limit(2) is inert because suppression guarantees ≤1 row;
#   round(chi2, 3)→4 changes display precision only.


def test_observed_scalar_all_aggregates():
    """_observed pure paths: rate (denominator-guarded), sum (sum_value with
    numerator fallback), mean (n-guarded) and the explicit aggregate override."""
    from types import SimpleNamespace

    from app.experiments.services.guardrails import GuardrailService

    observed = GuardrailService._observed
    rate_def = SimpleNamespace(kind="rate", spec={})
    assert observed(rate_def, {"numerator": 3, "denominator": 4}) == pytest.approx(0.75)
    assert observed(rate_def, {"numerator": 3, "denominator": 0}) is None
    cont_def = SimpleNamespace(kind="continuous", spec={})
    assert observed(cont_def, {"n": 4, "sum_value": 10.0}) == pytest.approx(2.5)
    assert observed(cont_def, {"n": 0, "sum_value": 10.0}) is None
    sum_def = SimpleNamespace(kind="continuous", spec={"guardrail_aggregate": "sum"})
    assert observed(sum_def, {"sum_value": 7.5}) == pytest.approx(7.5)
    assert observed(sum_def, {"numerator": 5}) == pytest.approx(5.0)  # fallback
    assert observed(sum_def, {}) == pytest.approx(0.0)
    # explicit rate override on a continuous definition
    rate_override = SimpleNamespace(kind="continuous", spec={"guardrail_aggregate": "rate"})
    assert observed(rate_override, {"numerator": 1, "denominator": 2}) == pytest.approx(0.5)
    # fuzz-found: a denormal denominator overflows the division to inf →
    # not evaluable (a non-finite observed would crash the Numeric write)
    assert observed(rate_def, {"numerator": 1e308, "denominator": 5e-324}) is None
    assert observed(sum_def, {"sum_value": float("inf")}) is None
    assert observed(cont_def, {"n": 5e-324, "sum_value": 1e308}) is None


async def test_launch_checklist_required_to_schedule(db):
    """§5 v2: scheduling without the affirmed checklist is refused with the
    missing items named; learning-domain experiments also require the ethics
    screen."""
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    await svc.create_version(exp.id, spec=_spec(), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    import pytest as _pytest

    from app.exceptions import AppError as _AppError

    with _pytest.raises(_AppError) as e:
        await svc.transition(exp.id, to_status="scheduled", actor=admin)
    assert e.value.code == "EXPERIMENT_CHECKLIST_INCOMPLETE"
    assert "ethics_screened" in e.value.message  # learning domain
    partial = {key: True for key in LAUNCH_CHECKLIST_KEYS}  # no ethics screen
    with _pytest.raises(_AppError) as e:
        await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=partial)
    assert "ethics_screened" in e.value.message
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    assert (await svc.get(exp.id)).status == "scheduled"


async def test_exposure_srm_alerts_on_trigger_bias(db):
    """§4.13 v2: exposures concentrated in ONE arm while assignments are
    balanced → __exposure_srm__ alert (never a pause) with dedup."""
    from app.experiments.models.guardrail import EXPOSURE_SRM_GUARDRAIL_KEY

    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    exposed = 0
    for i in range(200):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"es-{i}")
        if r is not None and r.variant_key == "treatment" and exposed < 80:
            await asvc.record_exposure(
                experiment_key=exp.key, unit_type="user", unit_id=f"es-{i}"
            )
            exposed += 1
    assert exposed >= 60
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "exposure_srm" in summary
    assert (await db.get(Experiment, exp.id)).status == "running"  # alert-only
    events = await GuardrailService(db).list_events(exp.id)
    hits = [e for e in events if e.guardrail_key == EXPOSURE_SRM_GUARDRAIL_KEY]
    assert len(hits) == 1 and hits[0].action == "alerted"
    # Dedup within the suppression window
    await GuardrailService(db).evaluate_experiment(exp.id)
    events = await GuardrailService(db).list_events(exp.id)
    assert len([e for e in events if e.guardrail_key == EXPOSURE_SRM_GUARDRAIL_KEY]) == 1


async def test_exposure_srm_quiet_when_proportional(db):
    exp, _ = await _mk_running(db)
    asvc = AssignmentService(db)
    for i in range(120):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"ep-{i}")
        assert r is not None
        await asvc.record_exposure(experiment_key=exp.key, unit_type="user", unit_id=f"ep-{i}")
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "exposure_srm" not in summary


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


# ── Round-10 interaction defect #28: switchback must not false-SRM ───


async def test_switchback_experiment_never_srm_alerts(db):
    """Switchback assignments all carry the placeholder variant — a naive
    SRM chi-square against the spec weights would ALWAYS fire. Defect #28:
    SRM (and exposure-SRM) must skip switchback designs entirely."""
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="SB", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    spec = _spec(None)
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
    from app.experiments.services.assignment import AssignmentService

    asvc = AssignmentService(db)
    for i in range(150):  # well past SRM_MIN_ASSIGNMENTS
        assert await asvc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=f"sbsrm-{i:04d}"
        ) is not None
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "srm" not in summary
    events = list(
        (
            await db.execute(
                select(GuardrailEvent).where(GuardrailEvent.experiment_id == exp.id)
            )
        ).scalars()
    )
    assert events == []
    row = await db.get(Experiment, exp.id)
    assert row.status == "running"


async def test_srm_alert_notifies_owner_once_per_window(db):
    """Defect #38: alert-only findings reach the owner — one notification
    per dedup window (the suppressed re-check adds none)."""
    from sqlalchemy import func as _func
    from sqlalchemy import select as _select

    from app.models.notification import Notification

    exp, _ = await _mk_running(db)
    for i in range(150):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"nsrm-{i:03d}",
                variant_key="control", assigned_version=1, bucket=0,
            )
        )
    await db.flush()
    svc = GuardrailService(db)
    await svc.evaluate_experiment(exp.id)
    await svc.evaluate_experiment(exp.id)  # suppressed window — no second note

    count = (
        await db.execute(
            _select(_func.count()).where(
                Notification.user_id == exp.owner_user_id,
                Notification.type == "experiment_guardrail",
            )
        )
    ).scalar_one()
    assert count == 1


async def test_pause_survives_notification_db_failure(db, monkeypatch):
    """Defect #42 (the #41 class): the owner notification is ADDITIVE — if
    its write explodes at the DB level it must roll back to its own
    SAVEPOINT. Before the fix the failed flush poisoned the session, the
    pause write was lost at commit, and the breached experiment kept
    running while the worker retried into the same wall forever."""
    from sqlalchemy import text

    from app.services.notification import NotificationService

    async def _exploding_create(self, *a, **k):
        # a REAL statement failure on the same session — poisons it
        await self.db.execute(text("select * from __no_such_table__"))

    monkeypatch.setattr(NotificationService, "create", _exploding_create)

    exp, _ = await _mk_running(
        db,
        guardrails=[
            {"metric_key": "exposure_rate", "op": "lte", "threshold": 0.4,
             "window_hours": 24}
        ],
    )
    asvc = AssignmentService(db)
    for i in range(10):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user",
                               unit_id=f"nf-{i}")
        assert r is not None
        await asvc.record_exposure(experiment_key=exp.key, unit_type="user",
                                   unit_id=f"nf-{i}")
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"], "breach must still be detected"
    # the pause survived the notification failure AND the session is healthy
    await db.flush()
    assert (await db.get(Experiment, exp.id)).status == "paused"
    events = await GuardrailService(db).list_events(exp.id)
    assert any(e.action == "paused" and e.auto for e in events)


async def test_alert_notify_failure_never_blocks_the_finding(db, monkeypatch):
    """Round 77: _notify_alert's except arm — an exploding notification
    service logs and moves on; the SRM finding itself survives."""
    from app.services.notification import NotificationService

    async def _plain_boom(self, *a, **k):
        raise RuntimeError("notify transport down")

    monkeypatch.setattr(NotificationService, "create", _plain_boom)
    exp, _ = await _mk_running(db)
    for i in range(150):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"nf-a-{i:04d}",
                variant_key="control", assigned_version=1, bucket=i % 10_000,
            )
        )
    for i in range(10):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"nf-b-{i:04d}",
                variant_key="treatment", assigned_version=1, bucket=i % 10_000,
            )
        )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "srm" in summary  # the finding outlives the notify failure
    assert (await db.get(Experiment, exp.id)).status == "running"
