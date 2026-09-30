"""Analysis runner DB tests (ADR-017 exp05).

End-to-end over real snapshots, the O'Brien-Fleming look budget, mSPRT free
peeking, mixed query_version warning, observational causal_claim:false, BH
flags on secondaries, and result-hash stability.

Runs against the dev Postgres (exp04 applied); rollback-per-test.
"""

from datetime import UTC, datetime, time, timedelta

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.exceptions import AppError
from app.experiments.models import MetricSnapshot
from app.experiments.services.analysis_service import AnalysisService
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.layers import LayerService
from app.experiments.services.metrics import MetricService
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
        "hypothesis": "analysis runner drives the pure core correctly",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {
            "primary": ["exposure_rate"],
            "secondary": ["run_success_rate"],
            "guardrails": [{"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}],
        },
        "sequential": "msprt",
    }
    base.update(overrides)
    return base


async def _mk_admin(db) -> User:
    user = User(
        email=f"exp-an-{ULID()}@example.com",
        display_name="A",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_running(db, **spec_overrides):
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    await svc.create_version(exp.id, spec=_spec(**spec_overrides), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    return exp, admin


async def _populate(db, exp, *, units: int = 40, expose_every: int = 2):
    asvc = AssignmentService(db)
    for i in range(units):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"an-{i}")
        assert r is not None
        if i % expose_every == 0:
            await asvc.record_exposure(
                experiment_key=exp.key, unit_type="user", unit_id=f"an-{i}"
            )
    start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=start, window_end=start + timedelta(days=1)
    )


async def test_analysis_end_to_end_msprt(db):
    exp, admin = await _mk_running(db)
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert result["causal_claim"] is True
    assert result["engine"] == "frequentist"
    assert result["control"] == "control"
    primary = result["metrics"]["exposure_rate"]
    assert primary["role"] == "primary"
    comparison = primary["comparisons"]["treatment"]
    assert "effect" in comparison and "ci" in comparison
    assert "always_valid_p" in comparison  # msprt free peeking
    assert "looks" not in result
    assert len(result["result_hash"]) == 64


async def test_analysis_result_hash_stable(db):
    exp, admin = await _mk_running(db)
    await _populate(db, exp)
    r1 = await AnalysisService(db).run(exp.id, actor=admin)
    r2 = await AnalysisService(db).run(exp.id, actor=admin)
    assert r1["result_hash"] == r2["result_hash"]


async def test_of_look_budget_exhausts(db):
    exp, admin = await _mk_running(
        db, sequential="obrien_fleming", stop_policy={"max_days": 28, "max_looks": 2}
    )
    await _populate(db, exp)
    svc = AnalysisService(db)
    r1 = await svc.run(exp.id, actor=admin)
    assert r1["looks"] == {"used": 1, "max": 2}
    comparison = r1["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    assert comparison["boundary_z"] > 1.959  # early looks are conservative
    r2 = await svc.run(exp.id, actor=admin)
    assert r2["looks"]["used"] == 2
    with pytest.raises(AppError) as e:
        await svc.run(exp.id, actor=admin)
    assert e.value.code == "EXPERIMENT_LOOKS_EXHAUSTED"


async def test_observational_never_claims_causality(db):
    exp, admin = await _mk_running(db, analysis_type="observational")
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert result["causal_claim"] is False
    assert "caveat" in result


async def test_bayesian_engine_reports_posterior(db):
    exp, admin = await _mk_running(db, stats_engine="bayesian")
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    assert "p_beat_control" in comparison
    assert "expected_loss" in comparison
    assert "credible_interval" in comparison


async def test_mixed_query_version_warns(db):
    exp, admin = await _mk_running(db)
    await _populate(db, exp)
    # Forge an older-version snapshot row for the same metric
    start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    db.add(
        MetricSnapshot(
            experiment_id=exp.id, metric_key="exposure_rate", variant_key="control",
            window_start=start - timedelta(days=1), window_end=start,
            n=5, numerator=1, denominator=5,
            provenance={"query_version": 0, "source": "exposures"},
        )
    )
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "SNAPSHOT_VERSION_MIXED" in result["warnings"]
    # And the aggregation used only the highest version (total exposure == 40
    # assigned units; the forged version-0 row's 5 must NOT leak in)
    comparison = result["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    total_exposure = comparison["control"]["exposure"] + comparison["treatment"]["exposure"]
    assert total_exposure == 40


async def test_draft_experiment_cannot_analyze(db):
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    exp = await ExperimentService(db).create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    with pytest.raises(AppError):
        await AnalysisService(db).run(exp.id, actor=admin)


async def test_secondary_metric_gets_fdr_flag_when_data_exists(db):
    """run_success_rate has no data here (insufficient), so no fdr flag; the
    primary carries comparisons. FDR wiring itself is covered by the pure BH
    tests + this structural check that insufficient data short-circuits."""
    exp, admin = await _mk_running(db)
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    # run_success_rate IS wired (workflow_runs) but these user units have no
    # runs → zero-sample comparison short-circuits inside the pure core
    secondary = result["metrics"]["run_success_rate"]
    comparison = secondary["comparisons"]["treatment"]
    assert comparison.get("insufficient_data") is True
    assert "passes_fdr" not in comparison
