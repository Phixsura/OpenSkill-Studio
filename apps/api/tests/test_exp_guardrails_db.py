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


def _spec(guardrails: list[dict] | None = None, *, unit_type: str = "user") -> dict:
    return {
        "hypothesis": "guardrails pause unsafe experiments automatically",
        "unit_type": unit_type,
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


async def _mk_running(db, *, guardrails: list[dict] | None = None,
                      unit_type: str = "user"):
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
    await svc.create_version(exp.id, spec=_spec(guardrails, unit_type=unit_type),
                             actor=admin)
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
    # #63: an UNDEFINED metric key can no longer reach running (the schedule
    # gate refuses it) — the honest arms are a definition with an
    # unregistered source and one with no source declared at all
    sourceless_key = f"nosrc_{str(_ULID()).lower()[:10]}"
    await MetricSvc(db).ensure_seed_definitions()
    await MetricSvc(db).create_definition(
        key=probe_key, title="Unwired probe", kind="continuous",
        domain="operational", source_kind="service",
        spec={"source": "no_such_source"},
    )
    await MetricSvc(db).create_definition(
        key=sourceless_key, title="Sourceless probe", kind="continuous",
        domain="operational", source_kind="service", spec={},
    )
    exp, _ = await _mk_running(
        db, guardrails=[
            {"metric_key": sourceless_key, "op": "lte", "threshold": 1.0},
            {"metric_key": probe_key, "op": "lte", "threshold": 1.0},
        ]
    )
    await AssignmentService(db).resolve(
        experiment_key=exp.key, unit_type="user", unit_id="u" * 26
    )
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"] == []
    assert (await db.get(Experiment, exp.id)).status == "running"


async def test_quantile_enabled_guardrail_evaluates_p95(db):
    """#65: a quantiles-enabled continuous definition used as a guardrail
    made the window fold do 0 + dict (the source now emits value_histogram)
    — a TypeError that killed the WHOLE guardrail sweep. Histograms must
    fold as histograms, and a p-aggregate must guard the quantile itself."""
    from app.models.workflow_pack import WorkflowPackInstallation
    from app.models.workflow_run import RunStatus, WorkflowRun

    svc = MetricService(db)
    await svc.ensure_seed_definitions()
    await svc.update_definition("run_latency_ms", quantiles=[0.95])
    # p95 aggregate on the guardrail read
    from sqlalchemy import select as _select

    from app.experiments.models import MetricDefinition

    definition = (
        await db.execute(_select(MetricDefinition).where(
            MetricDefinition.key == "run_latency_ms"))
    ).scalar_one()
    definition.spec = {**definition.spec, "guardrail_aggregate": "p95"}
    await db.flush()

    exp, _ = await _mk_running(
        db, unit_type="workflow_installation",
        guardrails=[{"metric_key": "run_latency_ms", "op": "lte",
                     "threshold": 5_000.0, "window_hours": 24}],
    )
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}",
                           slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(name=f"o-{str(ULID()).lower()}",
                       slug=f"o-{str(ULID()).lower()}", tenant_id=tenant.id)
    db.add(org)
    await db.flush()
    installation = WorkflowPackInstallation(org_id=org.id, installed_version="1.0.0")
    db.add(installation)
    await db.flush()
    await AssignmentService(db).resolve(
        experiment_key=exp.key, unit_type="workflow_installation",
        unit_id=installation.id,
    )
    t0 = datetime.now(UTC) - timedelta(hours=1)
    # 19 fast runs + 1 slow: p95 rank 19 -> fast bucket, but ANY mean-based
    # read would stay low too; the slow run pushes p99. Use 10 fast + 10
    # slow so p95 lands in the slow bucket (rank 19 of 20) and BREACHES.
    for ms in [100] * 10 + [60_000] * 10:
        db.add(WorkflowRun(
            org_id=org.id, installation_id=installation.id,
            definition_snapshot={}, status=RunStatus.COMPLETED,
            created_at=t0, started_at=t0,
            finished_at=t0 + timedelta(milliseconds=ms),
        ))
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert [b["metric_key"] for b in summary["breaches"]] == ["run_latency_ms"]
    breach = summary["breaches"][0]
    # p95 of (10x100, 10x60000): rank 19 -> the 60000 bucket ([32768,65536))
    assert 32_768.0 <= breach["observed"] <= 65_536.0
    assert (await db.get(Experiment, exp.id)).status == "paused"
    # cleanup the shared seeded definition
    await svc.update_definition("run_latency_ms", clear_quantiles=True)
    definition.spec = {k: v for k, v in definition.spec.items()
                       if k != "guardrail_aggregate"}
    await db.flush()


async def test_guardrail_fold_and_exact_threshold_boundaries(db):
    """Wave-33: the cross-variant fold is a SUM (an inverted fold cancels
    asymmetric arms), and observed EXACTLY ON the threshold is safe under
    BOTH ops (lte breaches strictly above; gte strictly below). Arms are
    pinned by direct assignment: A 3 assigned/2 exposed, B 2 assigned/1
    exposed -> folded exposure rate exactly 3/5."""
    import pytest as _pytest

    from app.experiments.models import Experiment, ExperimentAssignment

    exp, _ = await _mk_running(
        db, guardrails=[
            {"metric_key": "exposure_rate", "op": "lte", "threshold": 0.6,
             "window_hours": 24},
        ]
    )
    svc = AssignmentService(db)
    plan = [("control", 3, 2), ("treatment", 2, 1)]
    for arm, assigned, exposed in plan:
        for i in range(assigned):
            unit = f"fb-{arm}-{i}" + "x" * 10
            db.add(ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=unit,
                variant_key=arm, assigned_version=1, bucket=0,
                is_holdout=False,
            ))
            await db.flush()
            if i < exposed:
                assert await svc.record_exposure(
                    experiment_key=exp.key, unit_type="user", unit_id=unit
                )
    # observed == 3/5 == 0.6 exactly: AT the lte threshold -> safe
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"] == []
    assert (await db.get(Experiment, exp.id)).status == "running"
    # nudge the threshold just below: 0.6 > 0.59 -> breach, observed pinned
    # EXACTLY (an inverted fold yields (2-1)/(3-2) == 1.0, not 0.6)
    exp2, _ = await _mk_running(
        db, guardrails=[
            {"metric_key": "exposure_rate", "op": "lte", "threshold": 0.59,
             "window_hours": 24},
        ]
    )
    for arm, assigned, exposed in plan:
        for i in range(assigned):
            unit = f"fb2-{arm}-{i}" + "x" * 9
            db.add(ExperimentAssignment(
                experiment_id=exp2.id, unit_type="user", unit_id=unit,
                variant_key=arm, assigned_version=1, bucket=0,
                is_holdout=False,
            ))
            await db.flush()
            if i < exposed:
                assert await svc.record_exposure(
                    experiment_key=exp2.key, unit_type="user", unit_id=unit
                )
    summary2 = await GuardrailService(db).evaluate_experiment(exp2.id)
    assert len(summary2["breaches"]) == 1
    assert summary2["breaches"][0]["observed"] == _pytest.approx(0.6)
    # gte: observed exactly ON the floor is safe too
    exp3, _ = await _mk_running(
        db, guardrails=[
            {"metric_key": "exposure_rate", "op": "gte", "threshold": 0.6,
             "window_hours": 24},
        ]
    )
    for arm, assigned, exposed in plan:
        for i in range(assigned):
            unit = f"fb3-{arm}-{i}" + "x" * 9
            db.add(ExperimentAssignment(
                experiment_id=exp3.id, unit_type="user", unit_id=unit,
                variant_key=arm, assigned_version=1, bucket=0,
                is_holdout=False,
            ))
            await db.flush()
            if i < exposed:
                assert await svc.record_exposure(
                    experiment_key=exp3.key, unit_type="user", unit_id=unit
                )
    summary3 = await GuardrailService(db).evaluate_experiment(exp3.id)
    assert summary3["breaches"] == []
    # unknown experiment -> typed 404 (status pinned)
    from app.exceptions import AppError as _AppError
    with _pytest.raises(_AppError) as e:
        await GuardrailService(db).evaluate_experiment("0" * 26)
    assert e.value.status_code == 404


async def test_cost_ceiling_guards_the_window_total(db):
    """#69: the cost ceiling must breach on the window TOTAL, not the mean
    per task — three cheap tasks plus one big one total 100.25 (over the
    100 ceiling) while the mean is ~25 (far under): only the sum semantics
    fires. Also kills the fold's Add->Sub mutant for sum aggregates (a
    negated fold yields a negative observed that never breaches an lte)."""
    from decimal import Decimal

    import pytest as _pytest

    from app.experiments.models import Experiment, ExperimentAssignment
    from app.models.evaluation import EvalType, EvaluationTask

    svc = MetricService(db)
    await svc.ensure_seed_definitions()
    # the shared test DB may hold the pre-#69 seed row — align it
    from sqlalchemy import select as _select

    from app.experiments.models import MetricDefinition
    definition = (
        await db.execute(_select(MetricDefinition).where(
            MetricDefinition.key == "cost_usd"))
    ).scalar_one()
    original_spec = dict(definition.spec)
    # #69 family audit: BOTH cost definitions seed the sum aggregate on a
    # fresh deployment (the shared test DB may hold older rows — assert on
    # the seed TEMPLATE, not the row)
    from app.experiments.services.metrics import SEED_METRIC_DEFINITIONS
    for seed in SEED_METRIC_DEFINITIONS:
        if seed["key"] in ("cost_usd", "internal_cost_usd"):
            assert seed["spec"].get("guardrail_aggregate") == "sum", seed["key"]
    definition.spec = {**definition.spec, "guardrail_aggregate": "sum"}
    await db.flush()
    try:
        exp, _ = await _mk_running(
            db, unit_type="organization",
            guardrails=[{"metric_key": "cost_usd", "op": "lte",
                         "threshold": 100.0, "window_hours": 24}],
        )
        from app.controlplane.models.tenant import TenantAccount
        from app.models.organization import Organization

        tenant = TenantAccount(name=f"t-{str(ULID()).lower()}",
                               slug=f"t-{str(ULID()).lower()}")
        db.add(tenant)
        await db.flush()
        org = Organization(name=f"o-{str(ULID()).lower()}",
                           slug=f"o-{str(ULID()).lower()}",
                           tenant_id=tenant.id)
        db.add(org)
        await db.flush()
        db.add(ExperimentAssignment(
            experiment_id=exp.id, unit_type="organization", unit_id=org.id,
            variant_key="control", assigned_version=1, bucket=0,
            is_holdout=False,
        ))
        for cost in (Decimal("0.25"), Decimal("0.25"), Decimal("0.25"),
                     Decimal("99.50")):
            db.add(EvaluationTask(org_id=org.id, type=EvalType.EXERCISE_TEXT,
                                  cost_usd=cost))
        await db.flush()
        summary = await GuardrailService(db).evaluate_experiment(exp.id)
        assert len(summary["breaches"]) == 1
        assert summary["breaches"][0]["observed"] == _pytest.approx(100.25)
        assert (await db.get(Experiment, exp.id)).status == "paused"
    finally:
        definition.spec = original_spec
        await db.flush()


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
    # Wave 51 (window df-guard trio): the same 120 rows are in-window, so
    # the windowed check must evaluate df = 9 too
    assert "srm_window" in summary
    assert summary["srm_window"]["df"] == 9


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
# Wave 51 (check_srm_window + webhook retry) adds the same classes for the
# windowed check (its df/expected/chi2/re-alert/limit/round guards mirror
# check_srm), plus:
#   assigned_at >= window_start boundary needs microsecond-exact timestamps;
#   webhook retry-loop index mutants (sleep-index shifts, sleep-before-first)
#     are timing-equivalent under the uniform schedule the tests patch in —
#     attempt COUNT and retry/no-retry semantics are pinned by the
#     5xx/429/4xx/exhaustion quartet in test_new_services.py.


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


async def test_schedule_refuses_undefined_metric_keys(db):
    """#63 (write-boundary law): a spec referencing a metric key with no
    definition — primary, guardrail or covariate — used to schedule fine and
    collect silent zeros forever. The schedule gate now refuses, naming the
    unknown keys."""
    import pytest as _pytest

    from app.exceptions import AppError as _AppError

    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="matching"
    )
    svc = ExperimentService(db)
    checklist = {
        "hypothesis_peer_checked": True, "power_computed": True,
        "metrics_reviewed": True, "rollback_owner_named": True,
    }

    slice_cursor = iter([(0, 9), (10, 19)])

    async def _try(spec_patch: dict) -> _AppError:
        exp = await svc.create(
            key=f"exp-{str(ULID()).lower()}", title="T", domain="matching",
            layer_key=layer.key, owner_user_id=admin.id,
        )
        spec = _spec()
        spec.update(spec_patch)
        await svc.create_version(exp.id, spec=spec, actor=admin)
        lo, hi = next(slice_cursor)
        await LayerService(db).allocate(
            layer_key=layer.key, experiment_id=exp.id,
            slice_start=lo, slice_end=hi,
        )
        await svc.transition(exp.id, to_status="review", actor=admin)
        with _pytest.raises(_AppError) as e:
            await svc.transition(exp.id, to_status="scheduled", actor=admin,
                                 checklist=checklist)
        return e.value

    err = await _try({"metrics": {
        "primary": ["typo_metric_xyz"],
        "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                        "threshold": 100.0}],
    }})
    assert err.code == "EXPERIMENT_UNKNOWN_METRICS"
    assert "typo_metric_xyz" in err.message

    err = await _try({"variance_reduction": {
        "method": "cuped",
        "covariate_metrics": ["revision_count", "typo_covariate_xyz"],
        "lookback_days": 14,
    }})
    assert err.code == "EXPERIMENT_UNKNOWN_METRICS"
    assert "typo_covariate_xyz" in err.message


async def test_schedule_gate_matrix_guardrail_exemption_and_risk(db):
    """Wave-31 kills over the schedule gate's guardrail-exemption AND
    high-risk clauses — every quadrant pinned:
    low+exempt-domain without guardrails schedules; low+NON-exempt without
    guardrails refuses (422 pinned); MEDIUM+exempt still refuses (the
    exemption is risk-AND-domain); high-risk needs a platform admin (403
    pinned) and SUCCEEDS with one."""
    import pytest as _pytest

    from app.exceptions import AppError as _AppError
    from app.models.user import User as _User
    from app.models.user import UserRole as _Role
    from app.models.user import UserStatus as _Status

    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    checklist = _CHECKLIST  # all keys incl. ethics (learning domain needs it)
    svc = ExperimentService(db)
    slice_cursor = iter([(0, 9), (10, 19), (20, 29), (30, 39), (40, 49)])

    async def _schedule(*, domain: str, risk_class: str, guardrails: bool,
                        actor=None):
        layer = await LayerService(db).create(
            key=f"lyr-{str(ULID()).lower()}", domain=domain
        )
        exp = await svc.create(
            key=f"exp-{str(ULID()).lower()}", title="G", domain=domain,
            layer_key=layer.key, owner_user_id=admin.id,
            risk_class=risk_class,
        )
        spec = _spec(
            [{"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}]
            if guardrails else []
        )
        spec["hypothesis"] = "guardrail exemption matrix pins the gate"
        await svc.create_version(exp.id, spec=spec, actor=admin)
        lo, hi = next(slice_cursor)
        await LayerService(db).allocate(
            layer_key=layer.key, experiment_id=exp.id,
            slice_start=lo, slice_end=hi,
        )
        await svc.transition(exp.id, to_status="review", actor=admin)
        return await svc.transition(
            exp.id, to_status="scheduled", actor=actor or admin,
            checklist=checklist,
        )

    # low + exempt domain + no guardrails -> schedules
    ok = await _schedule(domain="operational", risk_class="low", guardrails=False)
    assert ok.status == "scheduled"
    # low + NON-exempt domain + no guardrails -> refused
    with _pytest.raises(_AppError) as e:
        await _schedule(domain="learning", risk_class="low", guardrails=False)
    assert e.value.code == "EXPERIMENT_NO_GUARDRAILS"
    assert e.value.status_code == 422
    # MEDIUM + exempt domain + no guardrails -> STILL refused (risk AND domain)
    with _pytest.raises(_AppError) as e:
        await _schedule(domain="operational", risk_class="medium", guardrails=False)
    assert e.value.code == "EXPERIMENT_NO_GUARDRAILS"
    # high risk + non-admin actor -> 403
    student = _User(email=f"sg-{ULID()}@example.com", display_name="S",
                    role=_Role.STUDENT, status=_Status.ACTIVE)
    db.add(student)
    await db.flush()
    with _pytest.raises(_AppError) as e:
        await _schedule(domain="learning", risk_class="high", guardrails=True,
                        actor=student)
    assert e.value.code == "FORBIDDEN"
    assert e.value.status_code == 403
    # high risk + platform admin -> schedules
    ok = await _schedule(domain="learning", risk_class="high", guardrails=True)
    assert ok.status == "scheduled"


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


async def test_missing_version_row_pauses_like_poison_spec(db):
    """#84 (round 333): a RUNNING experiment whose current_version row is
    gone (corrupted edge state) was "skipped" WITHOUT a stamp — silently
    unguarded while running, and squatting a fairness-cap slot at the head
    of every sweep forever. It must take the poison-spec path: pause +
    stamp (§106.26 + the spec-unparseable safety law)."""
    from sqlalchemy import delete as sa_delete

    from app.experiments.models.experiment import ExperimentVersion

    exp, _ = await _mk_running(db)
    await db.execute(
        sa_delete(ExperimentVersion).where(
            ExperimentVersion.experiment_id == exp.id
        )
    )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"] == [{"metric_key": "__spec_missing__"}]
    row = await db.get(Experiment, exp.id)
    assert row.status == "paused"
    assert row.last_guardrail_check_at is not None


async def test_closure_cap_not_squatted_by_long_max_days(db):
    """#86 (round 340, the #85 class): the max_days due-check lived after
    the started_at-ordered cap — an OLDER running experiment with a long
    max_days squatted the capped slot while a newer, actually-due one
    starved. With cap=1 the due one must still close."""
    from datetime import timedelta as _td

    from app.experiments.worker import sweep_experiment_closures

    # older, NOT due (long max_days)
    squatter, _ = await _mk_running(db)
    sq = await db.get(Experiment, squatter.id)
    sq.started_at = datetime.now(UTC) - _td(days=30)
    # its spec default max_days=28 would make it DUE — give it a long one
    from app.experiments.models import ExperimentVersion as ExpVer

    v = (
        await db.execute(
            select(ExpVer).where(ExpVer.experiment_id == squatter.id,
                                 ExpVer.version == sq.current_version)
        )
    ).scalar_one()
    spec = dict(v.spec)
    spec["stop_policy"] = {"max_days": 365, "max_looks": 4}
    v.spec = spec
    # newer, DUE (default 28 days, started 29 days ago)
    due, _ = await _mk_running(db)
    du = await db.get(Experiment, due.id)
    du.started_at = datetime.now(UTC) - _td(days=29)
    await db.flush()
    # residue law: only our two run
    from sqlalchemy import update as _update

    await db.execute(
        _update(Experiment)
        .where(Experiment.status == "running",
               Experiment.id.notin_([squatter.id, due.id]))
        .values(status="paused")
    )
    closed = await sweep_experiment_closures(db, cap=1)
    assert closed == 1, "the long-max_days squatter must not shadow the due one"
    assert (await db.get(Experiment, due.id)).status == "completed"
    assert (await db.get(Experiment, squatter.id)).status == "running"


async def test_closure_default_max_days_is_exactly_28(db):
    """Wave 49 strengthening: the SQL COALESCE default must be exactly the
    schema default (28) — a spec stored WITHOUT stop_policy, started 28.5
    days ago, is due under 28 and NOT under 29."""
    from datetime import timedelta as _td

    from app.experiments.worker import sweep_experiment_closures

    exp, _ = await _mk_running(db)
    row = await db.get(Experiment, exp.id)
    row.started_at = datetime.now(UTC) - _td(days=28, hours=12)
    # strip stop_policy from the stored spec so COALESCE's default governs
    from app.experiments.models import ExperimentVersion as ExpVer

    v = (
        await db.execute(
            select(ExpVer).where(ExpVer.experiment_id == exp.id,
                                 ExpVer.version == row.current_version)
        )
    ).scalar_one()
    spec = dict(v.spec)
    spec.pop("stop_policy", None)
    v.spec = spec
    await db.flush()
    from sqlalchemy import update as _update

    await db.execute(
        _update(Experiment)
        .where(Experiment.status == "running", Experiment.id != exp.id)
        .values(status="paused")
    )
    closed = await sweep_experiment_closures(db)
    assert closed == 1
    assert (await db.get(Experiment, exp.id)).status == "completed"


async def test_srm_window_catches_late_randomization_break(db):
    """Defect #90: cumulative SRM dilutes a late break. 5000 balanced
    assignments from last week + 120 all-control in the last 24h: the
    cumulative chi2 is 2.8125 (quiet at p<0.001) while the 24h window is
    flagrant (chi2=120). Industry (Statsig/Eppo) slices SRM by time; a
    windowed check must alert under its own __srm_window__ key —
    alert-only, never a pause, dedup-windowed like cumulative SRM."""
    exp, _ = await _mk_running(db)
    week_ago = datetime.now(UTC) - timedelta(days=7)
    for i in range(2500):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"w90-a-{i:05d}",
                variant_key="control", assigned_version=1, bucket=i % 10_000,
                assigned_at=week_ago,
            )
        )
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"w90-b-{i:05d}",
                variant_key="treatment", assigned_version=1, bucket=i % 10_000,
                assigned_at=week_ago,
            )
        )
    for i in range(120):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"w90-c-{i:04d}",
                variant_key="control", assigned_version=1, bucket=i % 10_000,
            )
        )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    # Cumulative SRM must stay quiet (2620/2500, chi2 = 2.8125 < 10.83)
    assert "srm" not in summary, "cumulative SRM should be diluted here"
    # The 24h window must fire: 120/0 on a 50/50 spec, chi2 = 120, df = 1
    assert "srm_window" in summary, "windowed SRM must catch the late break"
    win = summary["srm_window"]
    assert win["counts"] == {"control": 120, "treatment": 0}
    assert win["total"] == 120
    assert win["df"] == 1
    assert win["chi2"] == pytest.approx(120.0, abs=1e-6)
    assert win["window_hours"] == 24
    assert (await db.get(Experiment, exp.id)).status == "running", "alert-only"
    events = await GuardrailService(db).list_events(exp.id)
    win_events = [e for e in events if e.guardrail_key == "__srm_window__"]
    assert len(win_events) == 1 and win_events[0].action == "alerted"
    # Dedup within the 24h re-alert window
    await GuardrailService(db).evaluate_experiment(exp.id)
    events = await GuardrailService(db).list_events(exp.id)
    assert len([e for e in events if e.guardrail_key == "__srm_window__"]) == 1


async def test_srm_window_quiet_below_min_sample(db):
    """Defect #90 guard-band: a thin 24h slice (under the window minimum)
    must not fire — small recent samples are noisy by nature."""
    exp, _ = await _mk_running(db)
    for i in range(99):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"w90t-{i:04d}",
                variant_key="control", assigned_version=1, bucket=i % 10_000,
            )
        )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "srm_window" not in summary


async def test_srm_window_fires_exactly_at_min_sample_boundary(db):
    """Wave 51 killer (L187 Lt->LtE): exactly SRM_WINDOW_MIN_ASSIGNMENTS
    in-window rows must still be tested — the minimum is inclusive."""
    exp, _ = await _mk_running(db)
    for i in range(100):
        db.add(
            ExperimentAssignment(
                experiment_id=exp.id, unit_type="user", unit_id=f"w51m-{i:04d}",
                variant_key="control", assigned_version=1, bucket=i % 10_000,
            )
        )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "srm_window" in summary
    assert summary["srm_window"]["total"] == 100


async def test_exposure_srm_window_catches_late_trigger_bias(db):
    """Defect #92 (the #90 argument applied to trigger bias): cumulative
    exposure-SRM dilutes a LATE bias. 944 balanced historical exposures +
    56 all-treatment in the last 24h: cumulative chi2 = 3.14 (quiet at
    p<0.001) while the 24h exposure slice is flagrant (chi2 = 56 against
    the assignment proportions). Alert-only under __exposure_srm_window__,
    dedup-windowed."""
    from app.experiments.models.assignment import ExperimentExposure

    exp, _ = await _mk_running(db)
    week_ago = datetime.now(UTC) - timedelta(days=7)
    rows: dict[str, list] = {"control": [], "treatment": []}
    for i in range(528):
        for vk in ("control", "treatment"):
            row = ExperimentAssignment(
                experiment_id=exp.id, unit_type="user",
                unit_id=f"x92-{vk[0]}-{i:04d}", variant_key=vk,
                assigned_version=1, bucket=i % 10_000, assigned_at=week_ago,
            )
            db.add(row)
            rows[vk].append(row)
    await db.flush()
    ids = {vk: [r.id for r in lst] for vk, lst in rows.items()}
    # 472/472 balanced historical exposures, well outside the window
    for vk in ("control", "treatment"):
        for aid in ids[vk][:472]:
            db.add(
                ExperimentExposure(
                    assignment_id=aid, experiment_id=exp.id,
                    occurred_at=week_ago,
                )
            )
    # 56 treatment-only exposures inside the window (distinct assignments)
    for aid in ids["treatment"][472:528]:
        db.add(
            ExperimentExposure(assignment_id=aid, experiment_id=exp.id)
        )
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "exposure_srm" not in summary, "cumulative must be diluted here"
    assert "exposure_srm_window" in summary, "windowed check must fire"
    win = summary["exposure_srm_window"]
    assert win["counts"] == {"control": 0, "treatment": 56}
    assert win["total_exposed"] == 56
    assert win["window_hours"] == 24
    assert (await db.get(Experiment, exp.id)).status == "running", "alert-only"
    events = await GuardrailService(db).list_events(exp.id)
    hits = [e for e in events if e.guardrail_key == "__exposure_srm_window__"]
    assert len(hits) == 1 and hits[0].action == "alerted"
    # Dedup within the suppression window
    await GuardrailService(db).evaluate_experiment(exp.id)
    events = await GuardrailService(db).list_events(exp.id)
    assert len([e for e in events if e.guardrail_key == "__exposure_srm_window__"]) == 1


async def test_exposure_srm_window_quiet_below_min_exposed(db):
    """Defect #92 guard-band: under 50 in-window exposed units → quiet."""
    from app.experiments.models.assignment import ExperimentExposure

    exp, _ = await _mk_running(db)
    rows = []
    for i in range(49):
        row = ExperimentAssignment(
            experiment_id=exp.id, unit_type="user", unit_id=f"x92t-{i:03d}",
            variant_key="control", assigned_version=1, bucket=i,
        )
        db.add(row)
        rows.append(row)
    await db.flush()
    for row in rows:
        db.add(ExperimentExposure(assignment_id=row.id, experiment_id=exp.id))
    await db.flush()
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert "exposure_srm_window" not in summary


async def test_record_exposure_refuses_holdout_units(db):
    """Defect #94: resolve() returns None for a holdout unit — it is never
    served — so an exposure for it is a caller bug. record_exposure accepted
    the write (True) and stored a garbage row against the __holdout__
    assignment, feeding last_exposure_at with non-serving traffic. Contract:
    fail-safe False, no row."""
    from sqlalchemy import func as _f
    from sqlalchemy import select as _sel

    from app.experiments.models.assignment import ExperimentExposure

    exp, _ = await _mk_running(db)
    db.add(
        ExperimentAssignment(
            experiment_id=exp.id, unit_type="user", unit_id="h94-unit",
            variant_key="__holdout__", assigned_version=1, bucket=1,
            is_holdout=True,
        )
    )
    await db.flush()
    ok = await AssignmentService(db).record_exposure(
        experiment_key=exp.key, unit_type="user", unit_id="h94-unit"
    )
    assert ok is False, "exposure for a never-served holdout unit must be refused"
    n = (
        await db.execute(
            _sel(_f.count()).select_from(ExperimentExposure).where(
                ExperimentExposure.experiment_id == exp.id
            )
        )
    ).scalar_one()
    assert n == 0, "no exposure row may be written for a holdout unit"


async def test_timeline_note_cap_per_experiment(db, monkeypatch):
    """Defect #99 (the round-267 accumulation-bomb law applied to notes):
    the notes surface had no cap — any read-scope member could write
    unbounded rows into the append-only events table. At the cap a new
    note is 422 EXPERIMENT_NOTE_CAP."""
    import pytest as _pytest

    import app.experiments.services.experiments as exps
    from app.exceptions import AppError as _AppError

    exp, admin = await _mk_running(db)
    svc = ExperimentService(db)
    monkeypatch.setattr(exps, "EXPERIMENT_NOTE_CAP", 3, raising=False)
    for i in range(3):
        await svc.add_note(exp.id, actor_user_id=admin.id, text=f"note {i}")
    with _pytest.raises(_AppError) as e:
        await svc.add_note(exp.id, actor_user_id=admin.id, text="one too many")
    assert e.value.code == "EXPERIMENT_NOTE_CAP"


async def test_note_cap_holds_under_concurrency(db, monkeypatch):
    """Defect #100: the #99 cap check was a bare COUNT — two concurrent
    transactions both read cap-1 and both insert (TOCTOU overshoot). The
    fix locks the experiment row (FOR UPDATE, the state machine's own
    idiom) before counting, so concurrent note writers serialize and the
    cap is exact."""
    import asyncio as _aio

    from sqlalchemy import func as _func

    import app.experiments.services.experiments as exps
    from app.exceptions import AppError as _AppError

    exp, admin = await _mk_running(db)
    await db.commit()  # the two writer sessions must SEE the experiment
    monkeypatch.setattr(exps, "EXPERIMENT_NOTE_CAP", 1, raising=False)

    # Force the overlap: both writers must pass the COUNT before either
    # inserts. With the FOR-UPDATE fix the second writer never reaches this
    # gate (it blocks on the row lock), so the first times out and proceeds.
    orig_record = exps.ExperimentService._record_event
    gate = _aio.Event()
    arrived: list[int] = []

    async def gated_record(self, *a, **k):
        arrived.append(1)
        if len(arrived) >= 2:
            gate.set()
        try:
            await _aio.wait_for(gate.wait(), timeout=1.0)
        except TimeoutError:
            pass
        return await orig_record(self, *a, **k)

    monkeypatch.setattr(exps.ExperimentService, "_record_event", gated_record)

    async def writer(tag: str) -> bool:
        async with AsyncSessionLocal() as s:
            svc = ExperimentService(s)
            try:
                await svc.add_note(exp.id, actor_user_id=admin.id, text=f"c100 {tag}")
                await s.commit()
                return True
            except _AppError:
                await s.rollback()
                return False

    results = await _aio.gather(writer("a"), writer("b"))
    assert sum(results) == 1, f"exactly one writer may land at cap=1, got {results}"
    n = (
        await db.execute(
            select(_func.count()).select_from(ExperimentEvent).where(
                ExperimentEvent.experiment_id == exp.id,
                ExperimentEvent.event_type == "note",
            )
        )
    ).scalar_one()
    assert n == 1, f"cap must be exact under concurrency, found {n} notes"
    # This test COMMITS (two sessions must see the experiment) — clean up,
    # or the leaked running experiment skews global sweeps in later tests
    from sqlalchemy import delete as _delete

    await db.execute(_delete(Experiment).where(Experiment.id == exp.id))
    await db.commit()
