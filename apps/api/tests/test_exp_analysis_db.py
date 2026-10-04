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


async def test_honesty_warnings_for_triggered_and_cuped(db):
    """Triggered analysis is APPLIED now (batch 26): the remaining honest
    caveats are the uncorrected dilution and any legacy snapshots computed
    before the exposed-population switch; CUPED without covariates warns."""
    exp, admin = await _mk_running(
        db,
        trigger={"analysis_population": "exposed"},
        variance_reduction={"covariate_metric": "exposure_rate", "method": "cuped"},
    )
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "TRIGGERED_ANALYSIS_UNAPPLIED" not in result["warnings"]
    assert "TRIGGERED_DILUTION_UNCORRECTED" in result["warnings"]
    # every snapshot carries the exposed marker → no mixed-population warning
    assert "TRIGGERED_SNAPSHOTS_MIXED_POPULATION" not in result["warnings"]
    assert "CUPED_COVARIATES_UNAVAILABLE" in result["warnings"]

    # a legacy snapshot without the marker flips the mixed warning on
    db.add(_snapshot(exp.id, "exposure_rate", "control",
                     datetime(2026, 8, 1, tzinfo=UTC),
                     n=10, numerator=1, denominator=10))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "TRIGGERED_SNAPSHOTS_MIXED_POPULATION" in result["warnings"]


async def test_triggered_analysis_population_is_exposed_units(db):
    """§4.7 applied: with analysis_population=exposed, snapshot denominators
    count EXPOSED units only, and provenance says so."""
    from sqlalchemy import select

    from app.experiments.models import MetricSnapshot as _Snap

    exp, admin = await _mk_running(db, trigger={"analysis_population": "exposed"})
    # 40 assigned, every second unit exposed (via _populate's expose_every=2)
    await _populate(db, exp)
    rows = [
        r
        for r in (
            await db.execute(
                select(_Snap).where(
                    _Snap.experiment_id == exp.id,
                    _Snap.metric_key == "exposure_rate",
                )
            )
        ).scalars()
    ]
    assert rows
    total_denominator = sum(int(r.denominator or 0) for r in rows)
    assert total_denominator == 20  # exposed units only, not the 40 assigned
    for row in rows:
        assert row.provenance["analysis_population"] == "exposed"
    del admin


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
    # wave-34: the PRIMARY must never enter the FDR pool either (a flipped
    # role predicate feeds primary p-values into BH and stamps passes_fdr)
    primary = result["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    assert "p" in primary or "always_valid_p" in primary
    assert "passes_fdr" not in primary


# ── Health checks (v2 batch 4, §4.13/§4.6): pre_balance, novelty, aa_probe ──


def _snapshot(exp_id, metric_key, variant, ws, **cols):
    return MetricSnapshot(
        experiment_id=exp_id, metric_key=metric_key, variant_key=variant,
        window_start=ws, window_end=ws + timedelta(days=1),
        provenance={"query_version": 1}, **cols,
    )


async def test_multi_degrade_to_single_cuped_warns(db):
    """#62: a TWO-covariate spec whose snapshots carry only ONE covariate
    (its partner's source has no provider, say) silently fell back to the
    single-covariate adjustment — the operator asked for a joint adjustment
    and heard nothing. The fallback must warn CUPED_MULTI_DEGRADED; the
    honest multi path (e2e test below) must NOT."""
    exp, admin = await _mk_running(
        db, variance_reduction={
            "method": "cuped",
            # cost_usd IS defined (passes the #63 schedule gate) but its
            # source has no covariate provider -> honest degrade
            "covariate_metrics": ["revision_count", "cost_usd"],
            "lookback_days": 14,
        },
        metrics={"primary": ["revision_count"], "secondary": [],
                 "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                 "threshold": 100.0}]},
    )
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    # only the FIRST covariate assembled: cov_* mirror filled, covariates map
    # carries one key — the multi core refuses (whole entry missing) and the
    # legacy single path engages
    db.add(_snapshot(exp.id, "revision_count", "control", ws,
                     n=200, sum_value=200.0, sum_sq=260.0,
                     cov_sum=200.0, cov_sum_sq=260.0, cov_xy_sum=230.0,
                     covariates={"revision_count": {
                         "sum": 200.0, "sum_sq": 260.0, "xy_sum": 230.0}}))
    db.add(_snapshot(exp.id, "revision_count", "treatment", ws,
                     n=200, sum_value=220.0, sum_sq=300.0,
                     cov_sum=201.0, cov_sum_sq=263.0, cov_xy_sum=235.0,
                     covariates={"revision_count": {
                         "sum": 201.0, "sum_sq": 263.0, "xy_sum": 235.0}}))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["revision_count"]["comparisons"]["treatment"]
    cuped = comparison.get("cuped")
    assert cuped is not None and cuped.get("mode") != "multi"
    assert "CUPED_MULTI_DEGRADED" in result["warnings"]
    assert "CUPED_COVARIATES_UNAVAILABLE" not in result["warnings"]


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
    # wave-34 (L854): a k==1 adjustment is not a DEGRADED multi
    assert "CUPED_MULTI_DEGRADED" not in result["warnings"]


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
    # wave-34: the normal-normal precision-weighted formula pinned exactly
    se = comparison["se"]
    expected_shrunk = (
        effect / (se * se) + prior["mean"] / (prior["sd"] * prior["sd"])
    ) / (1.0 / (se * se) + 1.0 / (prior["sd"] * prior["sd"]))
    assert shrunk == pytest.approx(expected_shrunk, rel=1e-9)
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


async def test_observational_analysis_attaches_did(db):
    """Observational + per-unit covariates → a DiD change-score block with
    the parallel-trends caveat; randomized analyses never carry one."""
    exp, admin = await _mk_running(
        db,
        analysis_type="observational",
        metrics={"primary": ["revision_count"], "secondary": [],
                 "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                 "threshold": 100.0}]},
    )
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    db.add(_snapshot(exp.id, "revision_count", "control", ws,
                     n=50, sum_value=100.0, sum_sq=220.0,
                     cov_sum=50.0, cov_sum_sq=60.0, cov_xy_sum=105.0))
    db.add(_snapshot(exp.id, "revision_count", "treatment", ws,
                     n=50, sum_value=200.0, sum_sq=830.0,
                     cov_sum=50.0, cov_sum_sq=60.0, cov_xy_sum=205.0))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert result["causal_claim"] is False
    did = result["metrics"]["revision_count"]["comparisons"]["treatment"]["did"]
    # control Δ = 2-1 = 1, treatment Δ = 4-1 = 3 → DiD = 2
    assert abs(did["effect"] - 2.0) < 1e-9
    assert "parallel-trends" in did["caveat"]


async def test_segment_analysis_is_informational_slice(db):
    """run(segment=...) aggregates ONLY that slice, claims no causality,
    consumes no OF look, and writes no analysis_look event; the default run
    never mixes segment rows in."""
    from sqlalchemy import select as _select

    from app.experiments.models import ExperimentEvent

    exp, admin = await _mk_running(db, sequential="obrien_fleming")
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    for segment, control_num, treatment_num in (
        ("", 50, 70), ("org:AAAA", 10, 30), ("org:BBBB", 40, 40),
    ):
        for variant, numerator in (("control", control_num), ("treatment", treatment_num)):
            db.add(MetricSnapshot(
                experiment_id=exp.id, metric_key="exposure_rate",
                variant_key=variant, segment=segment, window_start=ws,
                window_end=ws + timedelta(days=1),
                n=200, numerator=numerator, denominator=200,
                provenance={"query_version": 1},
            ))
    await db.flush()

    slice_result = await AnalysisService(db).run(
        exp.id, actor=admin, segment="org:AAAA"
    )
    assert slice_result["segment"] == "org:AAAA"
    assert slice_result["causal_claim"] is False
    comparison = slice_result["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    assert abs(comparison["effect"] - 0.10) < 1e-9  # (30-10)/200

    # no look event, no budget burn from the slice
    looks = list(
        (
            await db.execute(
                _select(ExperimentEvent).where(
                    ExperimentEvent.experiment_id == exp.id,
                    ExperimentEvent.event_type == "analysis_look",
                )
            )
        ).scalars()
    )
    assert looks == []

    # the default run sees ONLY the whole-population rows
    full = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = full["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    assert abs(comparison["effect"] - 0.10) < 1e-9  # (70-50)/200, segments excluded
    assert "segment" not in full


async def test_three_arm_experiment_end_to_end(db):
    """Multi-variant path: a 3-arm experiment assigns to all arms, analysis
    produces one comparison per treatment (against the single control), and
    the bandit suggestion spans all three arms."""
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="marketplace")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="3arm", domain="marketplace",
        layer_key=layer.key, owner_user_id=admin.id, risk_class="low",
    )
    spec = _spec(allocation_mode="bandit")
    spec["variants"] = [
        {"key": "control", "name": "C", "weight_bp": 4000, "is_control": True},
        {"key": "t1", "name": "T1", "weight_bp": 3000},
        {"key": "t2", "name": "T2", "weight_bp": 3000},
    ]
    await svc.create_version(exp.id, spec=spec, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)

    asvc = AssignmentService(db)
    seen = set()
    for i in range(120):
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"3a-{i}")
        assert r is not None
        seen.add(r.variant_key)
        if i % 2 == 0:
            await asvc.record_exposure(
                experiment_key=exp.key, unit_type="user", unit_id=f"3a-{i}"
            )
    assert seen == {"control", "t1", "t2"}

    start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=start, window_end=start + timedelta(days=1)
    )
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparisons = result["metrics"]["exposure_rate"]["comparisons"]
    assert set(comparisons) == {"t1", "t2"}
    for comparison in comparisons.values():
        assert "effect" in comparison
    bandit = result["bandit"]
    assert set(bandit["p_best"]) == {"control", "t1", "t2"}
    assert sum(bandit["suggested_weights_bp"].values()) == 10_000


async def test_corpus_prior_is_platform_admin_only(db):
    """Information boundary (#35): the corpus prior aggregates effects across
    the whole domain incl. other orgs — a non-platform actor's analysis runs
    without it (same data, no shrinkage context)."""
    from app.models.user import User as _User
    from app.models.user import UserRole as _Role
    from app.models.user import UserStatus as _Status

    exp, admin = await _mk_running(db)
    await _mk_decided_history(db, "learning", "exposure_rate", [0.02, 0.03, 0.04])
    await _populate(db, exp)
    with_prior = await AnalysisService(db).run(exp.id, actor=admin)
    assert "corpus_prior" in with_prior["metrics"]["exposure_rate"]["comparisons"]["treatment"]

    org_operator = _User(
        email=f"op-{ULID()}@example.com", display_name="Op",
        role=_Role.INSTRUCTOR, status=_Status.ACTIVE,
    )
    db.add(org_operator)
    await db.flush()
    without = await AnalysisService(db).run(exp.id, actor=org_operator)
    comparison = without["metrics"]["exposure_rate"]["comparisons"]["treatment"]
    assert "corpus_prior" not in comparison
    assert "shrunk_effect" not in comparison
    assert "effect" in comparison  # the analysis itself is untouched


# ── Round-23 mutation killers (analysis_service internals) ───────────


def test_compare_matrix_pins_none_coalescing_and_engines():
    """_compare direct matrix: every `x or 0.0` coalesce is REAL (None-laden
    arms behave as zeros → insufficient_data, never a crash), both engines
    per kind produce their signature fields, and the rate bayesian extras
    appear exactly when data suffices."""
    from app.experiments.services.analysis_service import AnalysisService

    compare = AnalysisService._compare  # noqa: SLF001 — direct unit pin

    none_arm = {"numerator": None, "denominator": None, "n": None,
                "sum_value": None, "sum_sq": None}
    good_bin = {"numerator": 60.0, "denominator": 200.0}
    # None-laden arms = zeros = insufficient, for every kind/engine
    for kind in ("binary", "rate", "time_to_event", "continuous"):
        for engine in ("frequentist", "bayesian"):
            result = compare(kind, engine, none_arm, dict(none_arm))
            assert result.get("insufficient_data") is True, (kind, engine)

    # binary frequentist vs bayesian signatures
    freq = compare("binary", "frequentist", {"numerator": 50.0, "denominator": 200.0}, good_bin)
    assert "p" in freq and "ci" in freq
    bayes = compare("binary", "bayesian", {"numerator": 50.0, "denominator": 200.0}, good_bin)
    assert "p_beat_control" in bayes
    # time_to_event carries the binary-at-horizon caveat
    tte = compare("time_to_event", "frequentist",
                  {"numerator": 50.0, "denominator": 200.0}, good_bin)
    assert "caveat" in tte
    # rate bayesian extras ride on sufficient data
    rate = compare("rate", "bayesian",
                   {"numerator": 50.0, "denominator": 200.0}, good_bin)
    assert "p_beat_control" in rate and "expected_loss" in rate
    assert rate["expected_loss"] >= 0.0
    # continuous engines
    cont_c = {"n": 50.0, "sum_value": 100.0, "sum_sq": 260.0}
    cont_t = {"n": 50.0, "sum_value": 150.0, "sum_sq": 500.0}
    freq_c = compare("continuous", "frequentist", cont_c, cont_t)
    assert "t" in freq_c or "z" in freq_c
    bayes_c = compare("continuous", "bayesian", cont_c, cont_t)
    assert "p_beat_control" in bayes_c

    # ── wave-23 exact-value pins (structural asserts kill no arithmetic or
    # coalesce mutant) ────────────────────────────────────────────────────
    import math as _m

    import pytest as _pytest

    from app.experiments.services import analysis as _stats

    assert freq["effect"] == _pytest.approx(60.0 / 200.0 - 50.0 / 200.0, rel=1e-12)
    assert freq_c["effect"] == _pytest.approx(150.0 / 50.0 - 100.0 / 50.0, rel=1e-12)
    # the rate-bayesian extras, formulas spelled by hand against the
    # frequentist read of the same arms
    base = compare("rate", "frequentist",
                   {"numerator": 50.0, "denominator": 200.0}, good_bin)
    se, effect = base["se"], base["effect"]
    z0 = effect / se
    assert rate["p_beat_control"] == _pytest.approx(_stats.norm_cdf(z0), rel=1e-12)
    assert rate["expected_loss"] == _pytest.approx(
        max(0.0,
            se * _m.exp(-z0 * z0 / 2.0) / _m.sqrt(2.0 * _m.pi)
            - effect * _stats.norm_sf(z0)),
        rel=1e-12,
    )
    assert rate["credible_interval"] == base["ci"]
    # se == 0 is REACHABLE (0/200 vs 0/200 is sufficient data, zero
    # variance): the guards must take the else-0 branches, never divide
    zero_rate = compare("rate", "bayesian",
                        {"numerator": 0.0, "denominator": 200.0},
                        {"numerator": 0.0, "denominator": 200.0})
    assert zero_rate["p_beat_control"] == _pytest.approx(0.5)
    assert zero_rate["expected_loss"] == 0.0
    # binary CUPED gates (round 142): k == 1 via the cov_* mirror has NO
    # mode key; k == 2 with a covariates map runs the multi core
    bin_c = {"numerator": 80.0, "denominator": 200.0,
             "cov_sum": 200.0, "cov_sum_sq": 420.0, "cov_xy_sum": 95.0}
    bin_t = {"numerator": 110.0, "denominator": 200.0,
             "cov_sum": 205.0, "cov_sum_sq": 440.0, "cov_xy_sum": 130.0}
    single = compare("binary", "frequentist", bin_c, bin_t,
                     covariate_keys=["c1"])
    assert single["cuped"] is not None and "mode" not in single["cuped"]
    cov_c = {"c1": {"sum": 200.0, "sum_sq": 420.0, "xy_sum": 95.0,
                    "xx": {"c2": 210.0}},
             "c2": {"sum": 180.0, "sum_sq": 400.0, "xy_sum": 88.0}}
    cov_t = {"c1": {"sum": 205.0, "sum_sq": 440.0, "xy_sum": 130.0,
                    "xx": {"c2": 215.0}},
             "c2": {"sum": 190.0, "sum_sq": 430.0, "xy_sum": 120.0}}
    multi = compare("binary", "frequentist",
                    {**bin_c, "covariates": cov_c},
                    {**bin_t, "covariates": cov_t},
                    covariate_keys=["c1", "c2"])
    assert multi["cuped"]["mode"] == "multi"
    assert set(multi["cuped"]["theta"]) == {"c1", "c2"}
    # k == 1 WITH a covariates map (the real compute path stores one even
    # for a single covariate) must STILL take the single-covariate branch —
    # the strict > 1 gate, pinned on binary AND continuous
    k1_map = {"c1": {"sum": 200.0, "sum_sq": 420.0, "xy_sum": 95.0}}
    k1_map_t = {"c1": {"sum": 205.0, "sum_sq": 440.0, "xy_sum": 130.0}}
    bin_k1 = compare("binary", "frequentist",
                     {**bin_c, "covariates": k1_map},
                     {**bin_t, "covariates": k1_map_t},
                     covariate_keys=["c1"])
    assert bin_k1["cuped"] is not None and "mode" not in bin_k1["cuped"]
    cont_k1 = compare("continuous", "frequentist",
                      {"n": 200.0, "sum_value": 80.0, "sum_sq": 80.0,
                       "cov_sum": 200.0, "cov_sum_sq": 420.0,
                       "cov_xy_sum": 95.0, "covariates": k1_map},
                      {"n": 200.0, "sum_value": 110.0, "sum_sq": 110.0,
                       "cov_sum": 205.0, "cov_sum_sq": 440.0,
                       "cov_xy_sum": 130.0, "covariates": k1_map_t},
                      covariate_keys=["c1"])
    assert cont_k1["cuped"] is not None and "mode" not in cont_k1["cuped"]
    # the continuous t depends on sum_sq — pins the or-coalesce there
    assert freq_c["t"] == _pytest.approx(
        _stats.welch_from_stats(50.0, 100.0, 260.0, 50.0, 150.0, 500.0)["t"],
        rel=1e-12,
    )
    assert freq_c["t"] != 0.0


async def test_aggregate_uses_only_the_highest_query_version_values(db):
    """Version filter killer: the aggregate must EQUAL the v2 rows alone —
    not v1+v2 — and the mixed flag trips."""
    exp, admin = await _mk_running(db)
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    for version, numerator in ((1, 500), (2, 30)):
        for variant in ("control", "treatment"):
            db.add(MetricSnapshot(
                experiment_id=exp.id, metric_key="exposure_rate",
                variant_key=variant, window_start=ws + timedelta(days=version),
                window_end=ws + timedelta(days=version + 1),
                n=100, numerator=numerator, denominator=100,
                provenance={"query_version": version},
            ))
    await db.flush()
    aggregated, mixed = await AnalysisService(db)._aggregate_metric(  # noqa: SLF001
        exp.id, "exposure_rate"
    )
    assert mixed is True
    assert aggregated["treatment"]["numerator"] == 30.0  # v2 only, never 530
    assert aggregated["treatment"]["denominator"] == 100.0


async def test_novelty_thresholds_boundaries(db):
    """Novelty boundaries: 29-per-arm halves stay quiet (min 30), and a late
    effect EXACTLY one third of the early one is NOT decay (strict <)."""
    from sqlalchemy import delete

    exp, admin = await _mk_running(db)
    base = datetime(2026, 9, 1, tzinfo=UTC)

    async def _seed(denominator: int, early_num: int, late_num: int, control_num: int):
        await db.execute(delete(MetricSnapshot).where(
            MetricSnapshot.experiment_id == exp.id,
        ))
        for day in range(4):
            ws = base + timedelta(days=day)
            for variant in ("control", "treatment"):
                if variant == "control":
                    numerator = control_num
                else:
                    numerator = early_num if day < 2 else late_num
                db.add(MetricSnapshot(
                    experiment_id=exp.id, metric_key="exposure_rate",
                    variant_key=variant, window_start=ws,
                    window_end=ws + timedelta(days=1),
                    n=denominator, numerator=numerator, denominator=denominator,
                    provenance={"query_version": 1},
                ))
        await db.flush()

    # 28 per arm per HALF (14 per window × 2): below the 30 minimum —
    # quiet even with a huge decay
    await _seed(14, 13, 1, 1)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "NOVELTY_EFFECT_DECAY_SUSPECT" not in result["warnings"]

    # the one-third ratio from clearly ABOVE (no decay) and clearly BELOW
    # (decay) — the exact ==1/3 instant is float-unstable and ledgered as a
    # float-exact boundary (the round-6 class)
    await _seed(200, 100, 65, 40)   # late 0.125 > 0.30/3 → quiet
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "NOVELTY_EFFECT_DECAY_SUSPECT" not in result["warnings"]
    await _seed(200, 100, 50, 40)   # late 0.05 < 0.10 → flagged
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "NOVELTY_EFFECT_DECAY_SUSPECT" in result["warnings"]


async def test_single_version_never_flags_mixed(db):
    """len(versions) > 1 killer: a single query_version must not trip
    SNAPSHOT_VERSION_MIXED."""
    exp, admin = await _mk_running(db)
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "SNAPSHOT_VERSION_MIXED" not in result["warnings"]


async def test_corpus_prior_uses_latest_look_and_exact_sd(db):
    """Corpus killers: per historical experiment the LATEST look wins (an
    older look with a wild effect is ignored), and the prior's sd is the
    exact sample standard deviation."""
    from app.experiments.models import DecisionRecord, ExperimentEvent

    exp, admin = await _mk_running(db)
    layer_admin = admin
    svc = ExperimentService(db)
    from ulid import ULID as _ULID

    effects = [0.02, 0.03, 0.04]
    for i, effect in enumerate(effects):
        hist = await svc.create(
            key=f"hist-{str(_ULID()).lower()}", title="H", domain="learning",
            layer_key=exp.layer_key, owner_user_id=layer_admin.id,
        )
        # an OLD look with a wild effect, then the current one — latest wins
        db.add(ExperimentEvent(
            experiment_id=hist.id, actor_user_id=layer_admin.id,
            event_type="analysis_look",
            payload={"result_hash": "0" * 64, "primary_effects": {
                "exposure_rate": {"treatment": {"effect": 9.9, "se": 0.01}},
            }},
            created_at=datetime(2026, 8, 1, tzinfo=UTC),
        ))
        db.add(ExperimentEvent(
            experiment_id=hist.id, actor_user_id=layer_admin.id,
            event_type="analysis_look",
            payload={"result_hash": "1" * 64, "primary_effects": {
                "exposure_rate": {"treatment": {"effect": effect, "se": 0.01}},
            }},
            created_at=datetime(2026, 9, 1 + i, tzinfo=UTC),
        ))
        db.add(DecisionRecord(
            experiment_id=hist.id, experiment_version=1, decision="promote",
            summary="hist", domain="learning", analysis_type="randomized",
            analysis_result_hash="1" * 64, approver_user_id=layer_admin.id,
        ))
    await db.flush()
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    prior = result["metrics"]["exposure_rate"]["comparisons"]["treatment"]["corpus_prior"]
    assert prior["n_experiments"] == 3
    assert abs(prior["mean"] - 0.03) < 1e-12          # 9.9 never leaked in
    assert abs(prior["sd"] - 0.01) < 1e-12            # exact sample sd


# Wave-10 survivor ledger: the query_version .get(..., 1) defaults are
# unreachable (compute always stamps the version); the per-window None
# coalesces in _time_strata/_novelty mirror the snapshot-column templates
# (round-6 class — same-kind rows always carry their kind's fields); the
# novelty midpoint index and the exact ==1/3 and z==3 instants are
# float/index-exact boundaries.


async def test_concurrent_of_analyses_cannot_overspend_looks(db):
    """Defect #48: two committed sessions racing the LAST O'Brien-Fleming
    look — the row lock serializes them, so exactly one records the look and
    the other gets EXPERIMENT_LOOKS_EXHAUSTED. Before the fix both passed
    the max_looks gate and the budget was exceeded by one (alpha overspend
    beyond the spending plan)."""
    import asyncio

    from sqlalchemy import delete, func, select

    from app.core.database import AsyncSessionLocal
    from app.experiments.models import Experiment, ExperimentLayer

    exp, admin = await _mk_running(
        db, sequential="obrien_fleming", stop_policy={"max_days": 28, "max_looks": 1}
    )
    await _populate(db, exp, units=10)
    # the race needs COMMITTED state visible to two fresh sessions
    await db.commit()
    exp_id, layer_key, admin_id = exp.id, exp.layer_key, admin.id

    async def _analyze():
        async with AsyncSessionLocal() as session:
            from app.models.user import User as _User

            actor = await session.get(_User, admin_id)
            try:
                result = await AnalysisService(session).run(exp_id, actor=actor)
                await session.commit()
                return ("ok", result["looks"]["used"])
            except AppError as exc:
                return ("err", exc.code)

    try:
        results = await asyncio.gather(_analyze(), _analyze())
        outcomes = sorted(r[0] for r in results)
        assert outcomes == ["err", "ok"], results
        assert ("err", "EXPERIMENT_LOOKS_EXHAUSTED") in results
        assert ("ok", 1) in results
        # exactly ONE look event exists — the budget was never exceeded
        async with AsyncSessionLocal() as session:
            from app.experiments.models import ExperimentEvent as _Ev

            n = (
                await session.execute(
                    select(func.count()).where(
                        _Ev.experiment_id == exp_id,
                        _Ev.event_type == "analysis_look",
                    )
                )
            ).scalar_one()
            assert n == 1
    finally:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(Experiment).where(Experiment.id == exp_id))
            await session.execute(
                delete(ExperimentLayer).where(ExperimentLayer.key == layer_key)
            )
            from app.models.user import User as _User

            await session.execute(delete(_User).where(_User.id == admin_id))
            await session.commit()


async def test_power_block_and_underpowered_warning(db):
    """Round 46: a spec with a power target gets a payload power block from
    the OBSERVED control baseline — a 40-unit experiment against a 20%% MDE
    target is deeply underpowered, so SAMPLE_BELOW_POWER_TARGET must fire
    and powered must be False. A spec without power declares nothing."""
    exp, admin = await _mk_running(
        db, power={"mde": 0.20, "alpha": 0.05, "power": 0.8}
    )
    await _populate(db, exp)
    result = await AnalysisService(db).run(exp.id, actor=admin)
    block = result["power"]
    assert block["metric_key"] == "exposure_rate"
    assert block["required_n_per_arm"] > block["min_arm_n"] > 0
    assert block["powered"] is False
    assert "SAMPLE_BELOW_POWER_TARGET" in result["warnings"]
    assert 0 < block["baseline_rate"] < 1

    plain_exp, plain_admin = await _mk_running(db)
    await _populate(db, plain_exp)
    plain = await AnalysisService(db).run(plain_exp.id, actor=plain_admin)
    assert "power" not in plain
    assert "SAMPLE_BELOW_POWER_TARGET" not in plain["warnings"]


async def test_no_recent_exposures_warning(db):
    """Round 51: a RUNNING experiment with no exposures at all flags
    NO_RECENT_EXPOSURES (most often a broken integration, not a finished
    experiment); fresh exposures clear it."""
    exp, admin = await _mk_running(db)
    # assignments but ZERO exposures
    asvc = AssignmentService(db)
    for i in range(4):
        assert await asvc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=f"noexp-{i}"
        ) is not None
    start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=start, window_end=start + timedelta(days=1)
    )
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "NO_RECENT_EXPOSURES" in result["warnings"]

    fresh_exp, fresh_admin = await _mk_running(db)
    await _populate(db, fresh_exp)  # records exposures NOW
    fresh = await AnalysisService(db).run(fresh_exp.id, actor=fresh_admin)
    assert "NO_RECENT_EXPOSURES" not in fresh["warnings"]


async def test_auto_analysis_sweep_msprt_only_and_notifies_once(db):
    """Round 69: the daily sweep analyzes RUNNING mSPRT experiments (free
    peeking), notifies the owner once per day on significance, and NEVER
    touches an O'Brien-Fleming experiment (a robot must not spend a budgeted
    look)."""
    from sqlalchemy import func as _func
    from sqlalchemy import select as _select

    from app.experiments.models import ExperimentEvent
    from app.experiments.worker import sweep_experiment_analyses
    from app.models.notification import Notification

    # mSPRT with an overwhelming effect: all treatment units exposed, no
    # control units exposed
    exp, admin = await _mk_running(db)
    asvc = AssignmentService(db)
    for i in range(80):
        r = await asvc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=f"auto-{i}"
        )
        assert r is not None
        if r.variant_key == "treatment":
            await asvc.record_exposure(
                experiment_key=exp.key, unit_type="user", unit_id=f"auto-{i}"
            )
    start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=start, window_end=start + timedelta(days=1)
    )

    # an OF experiment that must NOT be analyzed by the robot
    of_exp, _ = await _mk_running(
        db, sequential="obrien_fleming", stop_policy={"max_days": 28, "max_looks": 2}
    )
    await _populate(db, of_exp)

    # §106.25: pause committed residue so the sweep sees OUR experiments only
    from sqlalchemy import update as _update

    from app.experiments.models import Experiment as _Exp

    await db.execute(
        _update(_Exp)
        .where(_Exp.status == "running", _Exp.id.notin_([exp.id, of_exp.id]))
        .values(status="paused")
    )
    analyzed = await sweep_experiment_analyses(db)
    assert analyzed == 1  # the mSPRT one, counted exactly once
    of_looks = (
        await db.execute(
            _select(_func.count()).where(
                ExperimentEvent.experiment_id == of_exp.id,
                ExperimentEvent.event_type == "analysis_look",
            )
        )
    ).scalar_one()
    assert of_looks == 0  # the OF budget is untouched

    notes = (
        await db.execute(
            _select(Notification).where(
                Notification.user_id == admin.id,
                Notification.type == "experiment_significance",
            )
        )
    ).scalars().all()
    assert len(notes) == 1
    assert notes[0].data["experiment_id"] == exp.id

    # second run the same day: analysis repeats, notification does NOT
    await sweep_experiment_analyses(db)
    n2 = (
        await db.execute(
            _select(_func.count()).where(
                Notification.user_id == admin.id,
                Notification.type == "experiment_significance",
            )
        )
    ).scalar_one()
    assert n2 == 1

    # the dedup window is 24h exactly: a notification older than that no
    # longer suppresses — backdate it and the sweep notifies again
    await db.execute(
        _update(Notification)
        .where(Notification.user_id == admin.id,
               Notification.type == "experiment_significance")
        .values(created_at=datetime.now(UTC) - timedelta(hours=24, minutes=30))
    )
    await sweep_experiment_analyses(db)
    n3 = (
        await db.execute(
            _select(_func.count()).where(
                Notification.user_id == admin.id,
                Notification.type == "experiment_significance",
            )
        )
    ).scalar_one()
    assert n3 == 2


async def test_auto_analysis_balanced_experiment_never_notifies(db):
    """Round 71 (wave-14 kills): a no-effect mSPRT experiment is analyzed
    but NEVER notifies — the significance gate is p present AND p < alpha,
    and the not-significant path must short-circuit before touching the
    (empty) significant list."""
    from sqlalchemy import func as _func
    from sqlalchemy import select as _select
    from sqlalchemy import update as _update

    from app.experiments.models import Experiment as _Exp
    from app.experiments.worker import sweep_experiment_analyses
    from app.models.notification import Notification

    exp, admin = await _mk_running(db)
    await _populate(db, exp)  # balanced: every other unit exposed, both arms
    await db.execute(
        _update(_Exp)
        .where(_Exp.status == "running", _Exp.id != exp.id)
        .values(status="paused")
    )
    analyzed = await sweep_experiment_analyses(db)
    assert analyzed == 1
    n = (
        await db.execute(
            _select(_func.count()).where(
                Notification.user_id == admin.id,
                Notification.type == "experiment_significance",
            )
        )
    ).scalar_one()
    assert n == 0


async def test_auto_analysis_poison_arms_never_stall_the_batch(db, monkeypatch):
    """Round 75 (coverage necropsy of the sweep's defensive arms): a stored
    unparseable spec AND a crashing analysis each skip their experiment and
    the batch continues — the healthy mSPRT experiment behind them is still
    analyzed, and the crash's session damage stays inside its savepoint."""
    from sqlalchemy import update as _update

    from app.experiments.models import Experiment as _Exp
    from app.experiments.models import ExperimentVersion as _Ver
    from app.experiments.worker import sweep_experiment_analyses

    # three running experiments, OLDEST ids first in the sweep order:
    poison_spec, _ = await _mk_running(db)
    crasher, _ = await _mk_running(db)
    healthy, _ = await _mk_running(db)
    await _populate(db, healthy)

    # (1) poison: corrupt the stored spec so model_validate fails
    await db.execute(
        _update(_Ver)
        .where(_Ver.experiment_id == poison_spec.id, _Ver.version == 1)
        .values(spec={"hypothesis": "x"})
    )
    # (2) crasher: analysis raises a REAL statement error on the session
    from app.experiments.services.analysis_service import AnalysisService as Svc

    original_run = Svc.run

    async def _maybe_boom(self, experiment_id, **kwargs):
        if experiment_id == crasher.id:
            from sqlalchemy import text as _text

            await self.db.execute(_text("select * from __no_table__"))
        return await original_run(self, experiment_id, **kwargs)

    monkeypatch.setattr(Svc, "run", _maybe_boom)

    await db.execute(
        _update(_Exp)
        .where(_Exp.status == "running",
               _Exp.id.notin_([poison_spec.id, crasher.id, healthy.id]))
        .values(status="paused")
    )
    analyzed = await sweep_experiment_analyses(db)
    assert analyzed == 1  # only the healthy one; neither arm stalled the batch
    await db.flush()  # the crash stayed inside its savepoint


async def test_analysis_spec_arms_necropsy(db):
    """Round 84: the analysis _spec arms — a dangling current_version (no
    matching row) is a typed 422, and a corrupted stored spec is a typed
    422 parse failure; neither leaks a raw 500."""
    from sqlalchemy import update as _update

    from app.experiments.models import Experiment as _Exp
    from app.experiments.models import ExperimentVersion as VersionModel

    exp, admin = await _mk_running(db)
    await _populate(db, exp, units=6)

    await db.execute(
        _update(_Exp).where(_Exp.id == exp.id).values(current_version=99)
    )
    with pytest.raises(AppError) as exc:
        await AnalysisService(db).run(exp.id, actor=admin)
    assert exc.value.code == "EXPERIMENT_SPEC_INVALID"
    assert "no spec version" in exc.value.message

    await db.execute(
        _update(_Exp).where(_Exp.id == exp.id).values(current_version=1)
    )
    await db.execute(
        _update(VersionModel)
        .where(VersionModel.experiment_id == exp.id, VersionModel.version == 1)
        .values(spec={"hypothesis": "nope"})
    )
    with pytest.raises(AppError) as exc:
        await AnalysisService(db).run(exp.id, actor=admin)
    assert exc.value.code == "EXPERIMENT_SPEC_INVALID"
    assert "failed to parse" in exc.value.message


async def test_latest_look_scorecard(db):
    """Round 87: the standing scorecard — None before any analysis, then the
    newest look with primary effects, the result hash a decision would
    reference, and the automated flag."""
    exp, admin = await _mk_running(db)
    svc = AnalysisService(db)
    assert await svc.latest_look(exp.id) is None
    await _populate(db, exp)
    first = await svc.run(exp.id, actor=admin)
    latest = await svc.latest_look(exp.id)
    assert latest is not None
    assert latest["result_hash"] == first["result_hash"]
    # a SECOND look: latest means newest, and exactly one row is read
    # (a widened limit makes scalar_one_or_none explode on two)
    second = await svc.run(exp.id, actor=admin)
    latest2 = await svc.latest_look(exp.id)
    assert latest2 is not None and latest2["result_hash"] == second["result_hash"]
    assert latest["sequential"] == "msprt"
    assert latest["automated"] is False
    assert "exposure_rate" in latest["primary_effects"]


async def test_multi_covariate_analysis_end_to_end(db):
    """§4.6 v3 round 115 (the epoch closes): a two-covariate spec flows
    snapshot -> aggregate -> joint adjustment; the comparison carries
    cuped.mode == "multi" with BOTH thetas."""
    from datetime import timedelta as _td

    from app.models.project import Project, Submission, SubmissionStatus
    from app.models.user import User as _User

    exp, admin = await _mk_running(db, variance_reduction={
        "method": "cuped",
        "covariate_metrics": ["revision_count", "project_approval_rate"],
        "lookback_days": 14,
    }, metrics={"primary": ["revision_count"],
                "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                "threshold": 100.0}]})
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}",
                           slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(name="mcv", slug=f"mcv-{str(ULID()).lower()}",
                       tenant_id=tenant.id)
    db.add(org)
    await db.flush()
    project = Project(org_id=org.id, title="MP",
                      slug=f"mp-{str(ULID()).lower()}", description="d",
                      instructions="i",
                      rubric=[{"criterion": "c", "max_score": 5}])
    db.add(project)
    await db.flush()

    from app.experiments.models.assignment import ExperimentAssignment

    window_start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    pre = window_start - _td(days=3)
    rng_rows = [
        # (pre_version, pre_status, window_version)
        (3, SubmissionStatus.APPROVED, 2),
        (2, SubmissionStatus.REJECTED, 3),
        (1, SubmissionStatus.APPROVED, 1),
        (4, SubmissionStatus.APPROVED, 2),
        (2, SubmissionStatus.REJECTED, 1),
        (3, SubmissionStatus.REJECTED, 4),
        (1, SubmissionStatus.APPROVED, 2),
        (2, SubmissionStatus.APPROVED, 3),
    ]
    from app.models.user import UserRole as _Role
    from app.models.user import UserStatus as _Status

    for i, (pv, pstat, wv) in enumerate(rng_rows):
        u = _User(email=f"mca-{i}-{ULID()}@example.com", display_name=f"A{i}",
                  role=_Role.STUDENT, status=_Status.ACTIVE)
        db.add(u)
        await db.flush()
        # #60: resolve() hash-buckets random ULIDs — ~7% of runs land an
        # arm with n <= 1 and BOTH adjustments rightly refuse (cert-92 flake).
        # Deterministic 4/4 split keeps the test about the covariate flow.
        db.add(ExperimentAssignment(
            experiment_id=exp.id, unit_type="user", unit_id=u.id,
            variant_key="control" if i % 2 == 0 else "treatment",
            assigned_version=1, bucket=0, is_holdout=False,
        ))
        db.add(Submission(org_id=org.id, project_id=project.id, user_id=u.id,
                          status=pstat, version=pv, created_at=pre))
        db.add(Submission(org_id=org.id, project_id=project.id, user_id=u.id,
                          status=SubmissionStatus.REJECTED, version=wv,
                          created_at=window_start + _td(hours=2)))
    await db.flush()
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=window_start, window_end=window_start + _td(days=1)
    )
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["revision_count"]["comparisons"]["treatment"]
    cuped = comparison.get("cuped")
    assert cuped is not None and cuped.get("mode") == "multi"
    assert set(cuped["theta"]) == {"revision_count", "project_approval_rate"}
    assert isinstance(cuped.get("variance_reduction_pct"), float)  # round 123
    # #62: the real joint adjustment ran — no degrade warning
    assert "CUPED_MULTI_DEGRADED" not in result["warnings"]


async def test_quantile_comparison_rides_the_analysis(db):
    """§4.14 round 124: snapshots carrying value_histogram fold across
    windows (counts add) and the continuous comparison gains a quantiles
    block for each probability the definition requests — informational,
    alongside the engine's primary comparison."""
    from sqlalchemy import select as _select

    from app.experiments.models import MetricDefinition

    exp, admin = await _mk_running(
        db, metrics={"primary": ["run_latency_ms"], "secondary": [],
                     "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                     "threshold": 100.0}]},
        unit_type="workflow_installation",
    )
    definition = (
        await db.execute(_select(MetricDefinition).where(
            MetricDefinition.key == "run_latency_ms"))
    ).scalar_one()
    definition.spec = {**definition.spec, "quantiles": [0.5]}
    await db.flush()
    ws1 = datetime(2026, 9, 1, tzinfo=UTC)
    ws2 = datetime(2026, 9, 2, tzinfo=UTC)
    # control ~100ms (bucket 6), treatment ~300ms (bucket 8); two windows
    # each so the fold is observable (counts double)
    for ws in (ws1, ws2):
        db.add(_snapshot(exp.id, "run_latency_ms", "control", ws,
                         n=10, sum_value=1000.0, sum_sq=110_000.0,
                         value_histogram={"6": 10}))
        db.add(_snapshot(exp.id, "run_latency_ms", "treatment", ws,
                         n=10, sum_value=3000.0, sum_sq=950_000.0,
                         value_histogram={"8": 10}))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["run_latency_ms"]["comparisons"]["treatment"]
    q = comparison["quantiles"]["0.5"]
    assert q["n_control"] == 20 and q["n_treatment"] == 20  # folded
    assert 64.0 <= q["control"] <= 128.0
    assert 256.0 <= q["treatment"] <= 512.0
    assert q["diff"] == pytest.approx(q["treatment"] - q["control"])
    assert "caveat" in q


async def test_look_history_lists_every_look_newest_first(db):
    """Round 137: the history view returns every recorded look, newest
    first, each entry shaped like latest_look; segment analyses stay out
    (they record no look)."""
    exp, admin = await _mk_running(db)
    await _populate(db, exp)
    svc = AnalysisService(db)
    first = await svc.run(exp.id, actor=admin)
    second = await svc.run(exp.id, actor=admin)
    history = await svc.look_history(exp.id)
    assert len(history) == 2
    # msprt looks carry no budget number (that is OF's) — order by recency
    assert history[0]["at"] >= history[1]["at"]
    assert history[0]["result_hash"] == second["result_hash"]
    assert history[1]["result_hash"] == first["result_hash"]
    assert history[0] == await svc.latest_look(exp.id)
    assert all(entry["automated"] is False for entry in history)
    assert len(await svc.look_history(exp.id, limit=1)) == 1
    # an OF look carries its budget number — pins the payload field mapping
    # (msprt looks are None there, so they cannot distinguish it)
    of_exp, of_admin = await _mk_running(db, sequential="obrien_fleming")
    await _populate(db, of_exp)
    await svc.run(of_exp.id, actor=of_admin)
    of_history = await svc.look_history(of_exp.id)
    assert len(of_history) == 1 and of_history[0]["look"] == 1
    assert of_history[0]["sequential"] == "obrien_fleming"


async def test_binary_cuped_rides_the_comparison(db):
    """Round 142: a binary primary under variance_reduction gains a cuped
    block (single covariate via the cov_* mirror) with the 0/1 caveat; the
    unadjusted engine result stays authoritative alongside."""
    exp, admin = await _mk_running(
        db, variance_reduction={"method": "cuped",
                                "covariate_metric": "revision_count",
                                "lookback_days": 14},
        metrics={"primary": ["project_approval_rate"], "secondary": [],
                 "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                 "threshold": 100.0}]},
    )
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    # per-unit binary snapshots: sum==sum_sq==numerator by construction
    db.add(_snapshot(exp.id, "project_approval_rate", "control", ws,
                     n=200, numerator=80.0, denominator=200.0,
                     cov_sum=200.0, cov_sum_sq=420.0, cov_xy_sum=95.0))
    db.add(_snapshot(exp.id, "project_approval_rate", "treatment", ws,
                     n=200, numerator=110.0, denominator=200.0,
                     cov_sum=205.0, cov_sum_sq=440.0, cov_xy_sum=130.0))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    comparison = result["metrics"]["project_approval_rate"]["comparisons"]["treatment"]
    assert "p" in comparison  # the unadjusted binary engine ran
    cuped = comparison.get("cuped")
    assert cuped is not None
    assert cuped["caveat"] == "linear adjustment on a per-unit 0/1 outcome"
    assert isinstance(cuped["variance_reduction_pct"], float)
    assert "CUPED_COVARIATES_UNAVAILABLE" not in result["warnings"]


async def test_aggregate_default_version_and_cross_window_covariate_fold(db):
    """Wave-34 kills: (B) a snapshot whose provenance LACKS query_version
    defaults to 1 and is correctly outvoted by a v2 row (mixed flagged);
    (C) the covariates map folds ACROSS WINDOWS — sums, xy and the xx cross
    terms all add (exact values pinned; an inverted fold cancels them)."""
    exp, admin = await _mk_running(db)
    ws1 = datetime(2026, 9, 1, tzinfo=UTC)
    ws2 = datetime(2026, 9, 2, tzinfo=UTC)
    svc = AnalysisService(db)

    # (B) versionless (defaults to 1) + explicit v2 -> v2 wins, mixed trips
    legacy = _snapshot(exp.id, "revision_count", "control", ws1,
                       n=10, sum_value=10.0, sum_sq=20.0)
    legacy.provenance = {}  # no query_version at all
    db.add(legacy)
    db.add(_snapshot(exp.id, "revision_count", "control", ws2,
                     n=7, sum_value=7.0, sum_sq=9.0))
    v2 = _snapshot(exp.id, "revision_count", "treatment", ws2,
                   n=5, sum_value=9.0, sum_sq=21.0)
    v2.provenance = {"query_version": 2}
    db.add(v2)
    await db.flush()
    aggregated, mixed = await svc._aggregate_metric(  # noqa: SLF001
        exp.id, "revision_count"
    )
    assert mixed is True
    assert set(aggregated) == {"treatment"}  # v2 outvotes BOTH v1-era rows
    assert aggregated["treatment"]["sum_value"] == 9.0

    # (B2) a LEGACY-ONLY metric (no query_version anywhere) must still
    # aggregate — the default constant pins itself when it is the only
    # version in play (a mutated default empties the aggregation)
    solo = _snapshot(exp.id, "run_success_rate", "control", ws1,
                     n=4, numerator=2.0, denominator=4.0)
    solo.provenance = {}
    db.add(solo)
    await db.flush()
    aggregated, mixed = await svc._aggregate_metric(  # noqa: SLF001
        exp.id, "run_success_rate"
    )
    assert mixed is False
    assert aggregated["control"]["denominator"] == 4.0

    # (C) two windows of covariates on a separate metric fold by addition
    for ws, scale in ((ws1, 1.0), (ws2, 2.0)):
        snap = _snapshot(exp.id, "exposure_rate", "control", ws,
                         n=10, sum_value=scale, sum_sq=scale,
                         covariates={
                             "c1": {"sum": 1.0 * scale, "sum_sq": 2.0 * scale,
                                    "xy_sum": 3.0 * scale,
                                    "xx": {"c2": 4.0 * scale}},
                             "c2": {"sum": 5.0 * scale, "sum_sq": 6.0 * scale,
                                    "xy_sum": 7.0 * scale},
                         })
        db.add(snap)
    await db.flush()
    aggregated, _mixed = await svc._aggregate_metric(  # noqa: SLF001
        exp.id, "exposure_rate"
    )
    cov = aggregated["control"]["covariates"]
    assert cov["c1"]["sum"] == 3.0 and cov["c1"]["xy_sum"] == 9.0
    assert cov["c1"]["xx"]["c2"] == 12.0
    assert cov["c2"]["sum"] == 15.0 and cov["c2"]["sum_sq"] == 18.0


async def test_power_boundary_and_recent_exposure_edge(db):
    """Wave-34: (H) min_arm_n EXACTLY at required_n_per_arm(10%, 20%) ==
    3841 is POWERED (the >= edge; the warning fires strictly below); (G)
    an exposure 47.5h old keeps the data-flow warning OFF while 48.5h
    trips it — pinning the 48h constant from both sides."""
    from app.experiments.models import ExperimentAssignment, ExperimentExposure

    exp, admin = await _mk_running(
        db, metrics={"primary": ["exposure_rate"], "secondary": [],
                     "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                     "threshold": 100.0}]},
        power={"mde": 0.20},
    )
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    # baseline EXACTLY 0.5 (num = den/2) -> required_n_per_arm(0.5, 0.2)
    # == 388, and each arm sits EXACTLY on that boundary
    for variant in ("control", "treatment"):
        db.add(_snapshot(exp.id, "exposure_rate", variant, ws,
                         n=388, numerator=194.0, denominator=388.0))
    # a FRESH exposure (47.5h is inside the 48h window)
    unit = "pw-" + "u" * 23
    db.add(ExperimentAssignment(
        experiment_id=exp.id, unit_type="user", unit_id=unit,
        variant_key="control", assigned_version=1, bucket=0, is_holdout=False,
    ))
    await db.flush()
    exposure = ExperimentExposure(
        assignment_id=None, experiment_id=exp.id, context={}, dedup_key=None,
    )
    # the exposure model needs the assignment id — fetch it
    from sqlalchemy import select as _select
    assignment = (
        await db.execute(_select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == exp.id))
    ).scalars().first()
    exposure.assignment_id = assignment.id
    db.add(exposure)
    await db.flush()
    exposure.occurred_at = datetime.now(UTC) - timedelta(hours=47, minutes=30)
    await db.flush()

    result = await AnalysisService(db).run(exp.id, actor=admin)
    block = result["power"]
    assert block["required_n_per_arm"] == 388
    assert block["powered"] is True  # EXACTLY at the boundary
    assert "SAMPLE_BELOW_POWER_TARGET" not in result["warnings"]
    assert "NO_RECENT_EXPOSURES" not in result["warnings"]

    # push the exposure past 48h -> the warning trips (and 49h-constant
    # mutants keep it fresh)
    exposure.occurred_at = datetime.now(UTC) - timedelta(hours=48, minutes=30)
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "NO_RECENT_EXPOSURES" in result["warnings"]


async def test_one_armed_metric_is_insufficient_and_n2_prebalance_runs(db):
    """Wave-34: (L598) snapshots for ONLY the treatment arm are
    insufficient data, never a KeyError on the missing control; (L623) the
    pre-balance check runs at n EXACTLY 2 per arm (the >= edge) — a
    flagrant covariate imbalance at n=2 still trips PRE_BALANCE_SUSPECT."""
    exp, admin = await _mk_running(db, power={"mde": 0.2})
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    db.add(_snapshot(exp.id, "exposure_rate", "treatment", ws,
                     n=10, numerator=5.0, denominator=10.0))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert result["metrics"]["exposure_rate"].get("insufficient_data") is True
    assert "power" not in result  # nothing computable without a control arm

    exp2, admin2 = await _mk_running(
        db, power={"mde": 0.2},  # a denominator-less continuous primary
        metrics={"primary": ["revision_count"], "secondary": [],
                 "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                 "threshold": 100.0}]},
    )
    db.add(_snapshot(exp2.id, "revision_count", "control", ws,
                     n=2, sum_value=2.0, sum_sq=2.5,
                     cov_sum=2.0, cov_sum_sq=2.5, cov_xy_sum=2.0))
    # near-zero within-arm variance makes t ~ 2000 at df ~ 1: even the
    # heavy df-1 tail puts p well under 0.001
    db.add(_snapshot(exp2.id, "revision_count", "treatment", ws,
                     n=2, sum_value=2.2, sum_sq=2.9,
                     cov_sum=2000.0, cov_sum_sq=2000000.0002,
                     cov_xy_sum=2.0))
    await db.flush()
    result2 = await AnalysisService(db).run(exp2.id, actor=admin2)
    assert "PRE_BALANCE_SUSPECT" in result2["warnings"]
    assert "power" not in result2  # continuous primary has no denominator


def test_analysis_service_error_status_contract_pinned():
    """Wave-34: the AST error-status contract, extended to the analysis
    service (the experiments.py pin does not cover this file)."""
    import ast
    from pathlib import Path

    src = (
        Path(__file__).resolve().parents[1]
        / "app" / "experiments" / "services" / "analysis_service.py"
    )
    found: dict[str, set[int]] = {}
    for node in ast.walk(ast.parse(src.read_text(encoding="utf-8"))):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "AppError"
            and len(node.args) >= 3
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[2], ast.Constant)
        ):
            found.setdefault(node.args[0].value, set()).add(node.args[2].value)
    assert found == {
        "EXPERIMENT_NOT_FOUND": {404},
        "EXPERIMENT_SPEC_INVALID": {422},
        "VALIDATION_ERROR": {422},
        "EXPERIMENT_LOOKS_EXHAUSTED": {422},
    }, found


async def test_corpus_and_did_guards_tolerate_degenerate_entries(db):
    """Wave-34: the corpus-prior and DiD blocks must SKIP degenerate
    entries, never crash — an insufficient primary (no comparisons) in a
    domain with a standing corpus, a zero-variance comparison (se == 0),
    and an observational run whose primary has one arm."""
    # standing corpus (3 decided experiments) comes from the shrink test's
    # domain fixtures — build our own three quickly
    exp0, admin = await _mk_running(db)
    ws = datetime(2026, 9, 1, tzinfo=UTC)

    # (a) insufficient primary in a corpus-bearing domain: no crash, no prior
    db.add(_snapshot(exp0.id, "exposure_rate", "treatment", ws,
                     n=10, numerator=5.0, denominator=10.0))
    await db.flush()
    result = await AnalysisService(db).run(exp0.id, actor=admin)
    assert result["metrics"]["exposure_rate"].get("insufficient_data") is True

    # (b) zero-variance continuous primary: comparisons exist but se == 0 —
    # the corpus shrink must skip (division by zero otherwise)
    exp1, admin1 = await _mk_running(
        db, metrics={"primary": ["revision_count"], "secondary": [],
                     "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                     "threshold": 100.0}]},
    )
    for variant in ("control", "treatment"):
        db.add(_snapshot(exp1.id, "revision_count", variant, ws,
                         n=50, sum_value=100.0, sum_sq=200.0))  # var == 0
    await db.flush()
    result1 = await AnalysisService(db).run(exp1.id, actor=admin1)
    comparison = result1["metrics"]["revision_count"]["comparisons"]["treatment"]
    assert "shrunk_effect" not in comparison  # guarded, not crashed

    # (c) observational run with a one-armed primary: the DiD block skips
    exp2, admin2 = await _mk_running(db, analysis_type="observational")
    db.add(_snapshot(exp2.id, "exposure_rate", "treatment", ws,
                     n=10, numerator=5.0, denominator=10.0))
    await db.flush()
    result2 = await AnalysisService(db).run(exp2.id, actor=admin2)
    assert result2["causal_claim"] is False
    assert result2["metrics"]["exposure_rate"].get("insufficient_data") is True


async def test_corpus_guards_with_standing_prior(db):
    """Wave-34 (with the corpus PRIOR in place, which the guards need to be
    reachable): an insufficient primary skips the shrink without a
    KeyError; a zero-variance comparison (se == 0) skips without division
    by zero; a degenerate corpus (identical effects -> prior sd == 0) skips
    the whole shrink."""
    ws = datetime(2026, 9, 1, tzinfo=UTC)

    # (a) insufficient primary + standing prior -> guard skips
    exp_a, admin_a = await _mk_running(db)
    await _mk_decided_history(db, "learning", "exposure_rate", [0.02, 0.03, 0.04])
    db.add(_snapshot(exp_a.id, "exposure_rate", "treatment", ws,
                     n=10, numerator=5.0, denominator=10.0))
    await db.flush()
    result = await AnalysisService(db).run(exp_a.id, actor=admin_a)
    assert result["metrics"]["exposure_rate"].get("insufficient_data") is True

    # (b) zero-variance continuous primary (se == 0) with a prior standing
    exp_b, admin_b = await _mk_running(
        db, metrics={"primary": ["revision_count"], "secondary": [],
                     "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                     "threshold": 100.0}]},
    )
    await _mk_decided_history(db, "learning", "revision_count", [0.1, 0.2, 0.3])
    for variant in ("control", "treatment"):
        db.add(_snapshot(exp_b.id, "revision_count", variant, ws,
                         n=50, sum_value=100.0, sum_sq=200.0))  # var == 0
    await db.flush()
    result_b = await AnalysisService(db).run(exp_b.id, actor=admin_b)
    comp_b = result_b["metrics"]["revision_count"]["comparisons"]["treatment"]
    assert "shrunk_effect" not in comp_b

    # (c) IDENTICAL corpus effects: the empirical prior sd is FLOORED above
    # zero (discovered here — the sd <= 0 guard is defense-in-depth), so the
    # shrink still runs and pulls fully toward the degenerate corpus mean
    exp_c, admin_c = await _mk_running(
        db, metrics={"primary": ["run_success_rate"], "secondary": [],
                     "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                     "threshold": 100.0}]},
    )
    await _mk_decided_history(db, "learning", "run_success_rate",
                              [0.05, 0.05, 0.05])
    for variant, num in (("control", 20.0), ("treatment", 30.0)):
        db.add(_snapshot(exp_c.id, "run_success_rate", variant, ws,
                         n=100, numerator=num, denominator=100.0))
    await db.flush()
    result_c = await AnalysisService(db).run(exp_c.id, actor=admin_c)
    comp_c = result_c["metrics"]["run_success_rate"]["comparisons"]["treatment"]
    assert comp_c["corpus_prior"]["sd"] > 0  # the floor, pinned
    assert "shrunk_effect" in comp_c


async def test_power_block_skips_zero_denominator_and_k1_not_degraded(db):
    """Wave-34: a binary primary whose arms carry ZERO denominators is not
    evaluable for power (skip, never a division by zero); and a k==1
    variance_reduction run engages the single adjustment WITHOUT the
    CUPED_MULTI_DEGRADED warning (the strict > 1 gate)."""
    ws = datetime(2026, 9, 1, tzinfo=UTC)
    exp, admin = await _mk_running(db, power={"mde": 0.2})
    for variant in ("control", "treatment"):
        db.add(_snapshot(exp.id, "exposure_rate", variant, ws,
                         n=0, numerator=0.0, denominator=0.0))
    await db.flush()
    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert "power" not in result  # not evaluable, not crashed

    exp2, admin2 = await _mk_running(
        db, variance_reduction={"method": "cuped",
                                "covariate_metric": "revision_count",
                                "lookback_days": 14},
        metrics={"primary": ["revision_count"], "secondary": [],
                 "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                 "threshold": 100.0}]},
    )
    db.add(_snapshot(exp2.id, "revision_count", "control", ws,
                     n=200, sum_value=200.0, sum_sq=260.0,
                     cov_sum=200.0, cov_sum_sq=260.0, cov_xy_sum=230.0))
    db.add(_snapshot(exp2.id, "revision_count", "treatment", ws,
                     n=200, sum_value=220.0, sum_sq=300.0,
                     cov_sum=201.0, cov_sum_sq=263.0, cov_xy_sum=235.0))
    await db.flush()
    result2 = await AnalysisService(db).run(exp2.id, actor=admin2)
    comparison = result2["metrics"]["revision_count"]["comparisons"]["treatment"]
    assert "cuped" in comparison
    assert "CUPED_MULTI_DEGRADED" not in result2["warnings"]


async def test_its_rides_observational_analysis(db):
    """Round 178 (§10 v3 step 2): an OBSERVATIONAL run with daily source
    data gets an `its` block on its primary — a clear pre->post jump lands
    a significant level change with the association-only caveat; a
    randomized run never carries the block."""
    from app.models.project import Project, Submission, SubmissionStatus
    from app.models.user import User as _User
    from app.models.user import UserRole as _Role
    from app.models.user import UserStatus as _Status

    exp, admin = await _mk_running(
        db, analysis_type="observational",
        metrics={"primary": ["revision_count"], "secondary": [],
                 "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                 "threshold": 100.0}]},
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
    project = Project(org_id=org.id, title="IP",
                      slug=f"ip-{str(ULID()).lower()}", description="d",
                      instructions="i",
                      rubric=[{"criterion": "c", "max_score": 5}])
    db.add(project)
    await db.flush()
    unit = _User(email=f"its-{ULID()}@example.com", display_name="I",
                 role=_Role.STUDENT, status=_Status.ACTIVE)
    db.add(unit)
    await db.flush()
    from app.experiments.models import Experiment, ExperimentAssignment

    db.add(ExperimentAssignment(
        experiment_id=exp.id, unit_type="user", unit_id=unit.id,
        variant_key="treatment", assigned_version=1, bucket=0,
        is_holdout=False,
    ))
    exp_row = await db.get(Experiment, exp.id)
    start_day = (datetime.now(UTC) - timedelta(days=3)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    exp_row.started_at = start_day
    await db.flush()
    # pre: one v2 submission per day (1 revision); post: v4 (3 revisions)
    for offset in range(14, 0, -1):
        db.add(Submission(org_id=org.id, project_id=project.id,
                          user_id=unit.id, status=SubmissionStatus.APPROVED,
                          version=2,
                          created_at=start_day - timedelta(days=offset,
                                                           hours=-6)))
    for offset in range(3):
        db.add(Submission(org_id=org.id, project_id=project.id,
                          user_id=unit.id, status=SubmissionStatus.APPROVED,
                          version=4,
                          created_at=start_day + timedelta(days=offset,
                                                           hours=6)))
    # snapshots so the primary itself is computable
    ws = start_day + timedelta(days=1)
    for variant, total in (("control", 10.0), ("treatment", 14.0)):
        db.add(_snapshot(exp.id, "revision_count", variant, ws,
                         n=10, sum_value=total, sum_sq=total * 2.5))
    await db.flush()

    result = await AnalysisService(db).run(exp.id, actor=admin)
    assert result["causal_claim"] is False
    its = result["metrics"]["revision_count"].get("its")
    assert its is not None
    assert its["n_pre"] == 14 and its["n_post"] == 14
    # pre daily mean 1.0 (only 3 post days carry data; silent days are 0 —
    # the jump from 1.0-steady to a 3/0 mix still shifts the level)
    assert "association only" in its["caveat"]

    # randomized runs never carry the block
    exp_r, admin_r = await _mk_running(db)
    db.add(_snapshot(exp_r.id, "exposure_rate", "control", ws,
                     n=10, numerator=5.0, denominator=10.0))
    db.add(_snapshot(exp_r.id, "exposure_rate", "treatment", ws,
                     n=10, numerator=6.0, denominator=10.0))
    await db.flush()
    result_r = await AnalysisService(db).run(exp_r.id, actor=admin_r)
    assert "its" not in result_r["metrics"]["exposure_rate"]
