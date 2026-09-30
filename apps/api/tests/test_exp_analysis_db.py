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
from app.experiments.security import ETHICS_CHECKLIST_KEY, LAUNCH_CHECKLIST_KEYS
from app.experiments.services.analysis_service import AnalysisService
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.layers import LayerService
from app.experiments.services.metrics import MetricService
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
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
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


async def test_honesty_warnings_for_unapplied_knobs(db):
    """Spec knobs accepted but not yet applied must be SURFACED: triggered
    (exposed-only) analysis and CUPED without covariate data both warn."""
    exp, admin = await _mk_running(
        db,
        trigger={"analysis_population": "exposed"},
        variance_reduction={"covariate_metric": "exposure_rate", "method": "cuped"},
    )
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "TRIGGERED_ANALYSIS_UNAPPLIED" in result["warnings"]
    assert "CUPED_COVARIATES_UNAVAILABLE" in result["warnings"]


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


# ── Health checks (v2 batch 4, §4.13/§4.6): pre_balance, novelty, aa_probe ──


def _snapshot(exp_id, metric_key, variant, ws, **cols):
    return MetricSnapshot(
        experiment_id=exp_id, metric_key=metric_key, variant_key=variant,
        window_start=ws, window_end=ws + timedelta(days=1),
        provenance={"query_version": 1}, **cols,
    )


async def test_pre_balance_suspect_on_covariate_imbalance(db):
    """Covariates are pre-experiment by construction — arm means that differ
    (p < 0.001) mean broken randomization, and analysis must say so."""
    exp, admin = await _mk_running(
        db, metrics={"primary": ["revision_count"], "secondary": [],
                     "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                     "threshold": 100.0}]},
    )
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    db.add(_snapshot(exp.id, "revision_count", "control", ws,
                     n=200, sum_value=200.0, sum_sq=260.0,
                     cov_sum=200.0, cov_sum_sq=260.0, cov_xy_sum=500.0))
    db.add(_snapshot(exp.id, "revision_count", "treatment", ws,
                     n=200, sum_value=220.0, sum_sq=300.0,
                     cov_sum=1200.0, cov_sum_sq=7500.0, cov_xy_sum=500.0))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "PRE_BALANCE_SUSPECT" in result["warnings"]


async def test_pre_balance_quiet_when_covariates_match(db):
    exp, admin = await _mk_running(
        db, metrics={"primary": ["revision_count"], "secondary": [],
                     "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                     "threshold": 100.0}]},
    )
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    db.add(_snapshot(exp.id, "revision_count", "control", ws,
                     n=200, sum_value=200.0, sum_sq=260.0,
                     cov_sum=200.0, cov_sum_sq=260.0, cov_xy_sum=500.0))
    db.add(_snapshot(exp.id, "revision_count", "treatment", ws,
                     n=200, sum_value=220.0, sum_sq=300.0,
                     cov_sum=201.0, cov_sum_sq=263.0, cov_xy_sum=500.0))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "PRE_BALANCE_SUSPECT" not in result["warnings"]
    # CUPED engaged — the covariates are real, so no unavailability warning
    assert "cuped" in result["metrics"]["revision_count"]["comparisons"]["treatment"]


async def test_novelty_decay_flags_early_effect_that_vanishes(db):
    """Strong early binary effect (days 1-2) that disappears (days 3-4)
    → NOVELTY_EFFECT_DECAY_SUSPECT; a stable effect stays quiet."""
    from sqlalchemy import delete

    exp, admin = await _mk_running(db)
    base = datetime(2026, 9, 1, tzinfo=UTC)

    async def _seed(decaying: bool):
        await db.execute(
            delete(MetricSnapshot).where(
                MetricSnapshot.experiment_id == exp.id,
                MetricSnapshot.metric_key == "exposure_rate",
            )
        )
        for day in range(4):
            ws = base + timedelta(days=day)
            for variant in ("control", "treatment"):
                early = day < 2
                if variant == "control":
                    numerator = 50
                elif early:
                    numerator = 90            # huge early lift
                else:
                    numerator = 50 if decaying else 90
                db.add(_snapshot(exp.id, "exposure_rate", variant, ws,
                                 n=200, numerator=numerator, denominator=200))
        await db.flush()

    await _seed(decaying=True)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "NOVELTY_EFFECT_DECAY_SUSPECT" in result["warnings"]

    await _seed(decaying=False)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "NOVELTY_EFFECT_DECAY_SUSPECT" not in result["warnings"]


async def test_novelty_needs_enough_windows(db):
    """One or two windows can't split — no false decay alarm on day one."""
    exp, admin = await _mk_running(db)
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    for variant, numerator in (("control", 50), ("treatment", 90)):
        db.add(_snapshot(exp.id, "exposure_rate", variant, ws,
                         n=200, numerator=numerator, denominator=200))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "NOVELTY_EFFECT_DECAY_SUSPECT" not in result["warnings"]


def test_aa_probe_healthy_and_deterministic():
    from app.experiments.services.assignment import aa_probe

    probe = aa_probe("aa-golden-layer", n=5000)
    assert probe["healthy"] is True
    assert probe["n"] == 5000
    assert sum(probe["deciles"]) == 5000
    # deterministic: same inputs, same report
    assert aa_probe("aa-golden-layer", n=5000) == probe
    # bounds clamp
    assert aa_probe("aa-golden-layer", n=10)["n"] == 100


# ── Meta-analysis corpus prior (v2 batch 5, §11) ─────────────────────


async def _mk_decided_history(db, domain: str, metric_key: str, effects: list[float]):
    """Insert N historical decided experiments whose latest analysis_look
    carries the given primary effect."""
    from app.experiments.models import DecisionRecord, ExperimentEvent

    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain=domain)
    svc = ExperimentService(db)
    for effect in effects:
        exp = await svc.create(
            key=f"hist-{str(ULID()).lower()}", title="H", domain=domain,
            layer_key=layer.key, owner_user_id=admin.id,
        )
        db.add(ExperimentEvent(
            experiment_id=exp.id, actor_user_id=admin.id,
            event_type="analysis_look",
            payload={"result_hash": "0" * 64, "primary_effects": {
                metric_key: {"treatment": {"effect": effect, "se": 0.01}},
            }},
        ))
        db.add(DecisionRecord(
            experiment_id=exp.id, experiment_version=1, decision="promote",
            summary="hist", domain=domain, analysis_type="randomized",
            analysis_result_hash="0" * 64, approver_user_id=admin.id,
        ))
    await db.flush()


async def test_corpus_prior_shrinks_primary_effect(db):
    """With >= 3 decided same-domain experiments on the metric, comparisons
    carry the empirical prior and a normal-normal shrunk estimate pulled
    toward the corpus mean."""
    exp, admin = await _mk_running(db)
    await _mk_decided_history(db, "learning", "exposure_rate", [0.02, 0.03, 0.04])
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    prior = comparison["corpus_prior"]
    assert prior["n_experiments"] == 3
    assert abs(prior["mean"] - 0.03) < 1e-9
    assert prior["sd"] > 0
    effect, shrunk = comparison["effect"], comparison["shrunk_effect"]
    # shrunk lies strictly between the raw effect and the corpus mean
    low, high = sorted((effect, prior["mean"]))
    assert low <= shrunk <= high
    assert shrunk != effect or effect == prior["mean"]


async def test_corpus_prior_absent_below_three_and_cross_domain(db):
    exp, admin = await _mk_running(db)
    # only two decided experiments in-domain, three in ANOTHER domain
    await _mk_decided_history(db, "learning", "exposure_rate", [0.02, 0.03])
    await _mk_decided_history(db, "operational", "exposure_rate", [0.5, 0.6, 0.7])
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    assert "corpus_prior" not in comparison
    assert "shrunk_effect" not in comparison


async def test_analysis_look_records_primary_effects(db):
    from sqlalchemy import select as _select

    from app.experiments.models import ExperimentEvent

    exp, admin = await _mk_running(db)
    await _populate(db, exp)
    await AnalysisService(db).run(exp.id, actor=admin)
    event = (
        await db.execute(
            _select(ExperimentEvent).where(
                ExperimentEvent.experiment_id == exp.id,
                ExperimentEvent.event_type == "analysis_look",
            ).order_by(ExperimentEvent.created_at.desc()).limit(1)
        )
    ).scalar_one()
    recorded = event.payload["primary_effects"]["exposure_rate"]["treatment"]
    assert recorded["effect"] is not None
    assert recorded["se"] is not None


# ── Time-stratified estimate (v2 batch 8) ────────────────────────────


async def test_time_stratified_estimate_on_primary(db):
    """Two windows with a consistent lift → time_stratified pooled effect
    close to the naive one, with both windows counted; a single window
    yields no stratified estimate."""
    exp, admin = await _mk_running(db)
    base_ws = datetime(2026, 9, 1, tzinfo=UTC)
    for day in range(2):
        ws = base_ws + timedelta(days=day)
        db.add(_snapshot(exp.id, "exposure_rate", "control", ws,
                         n=200, numerator=50, denominator=200))
        db.add(_snapshot(exp.id, "exposure_rate", "treatment", ws,
                         n=200, numerator=70, denominator=200))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    stratified = comparison["time_stratified"]
    assert stratified["strata"] == 2
    assert abs(stratified["effect"] - 0.10) < 0.01
    assert stratified["se"] < comparison["se"] * 1.05  # pooling never blows up se


async def test_time_stratified_absent_with_one_window(db):
    exp, admin = await _mk_running(db)
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    db.add(_snapshot(exp.id, "exposure_rate", "control", ws,
                     n=200, numerator=50, denominator=200))
    db.add(_snapshot(exp.id, "exposure_rate", "treatment", ws,
                     n=200, numerator=70, denominator=200))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    assert "time_stratified" not in comparison


# ── Bandit suggestion in analysis (v2 batch 10) ──────────────────────


async def test_bandit_allocation_gets_thompson_suggestion(db):
    # bandit gate: marketplace domain + low risk only
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="marketplace")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="B", domain="marketplace",
        layer_key=layer.key, owner_user_id=admin.id, risk_class="low",
    )
    await svc.create_version(
        exp.id, spec=_spec(allocation_mode="bandit"), actor=admin
    )
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    db.add(_snapshot(exp.id, "exposure_rate", "control", ws,
                     n=500, numerator=50, denominator=500))
    db.add(_snapshot(exp.id, "exposure_rate", "treatment", ws,
                     n=500, numerator=120, denominator=500))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    bandit = result["bandit"]
    assert bandit["metric"] == "exposure_rate"
    assert bandit["p_best"]["treatment"] > 0.9
    assert sum(bandit["suggested_weights_bp"].values()) == 10_000
    # advisory only: the experiment's live weights are untouched
    versions = await svc.get_versions(exp.id)
    weights = {v["key"]: v["weight_bp"] for v in versions[-1].spec["variants"]}
    assert weights == {"control": 5000, "treatment": 5000}


async def test_fixed_allocation_has_no_bandit_block(db):
    exp, admin = await _mk_running(db)
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "bandit" not in result
