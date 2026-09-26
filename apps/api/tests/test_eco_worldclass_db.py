"""World-class-gap closure tests (2026-09-22 round 2).

Statistics kernel (Welch/z/CI/Bradley-Terry/semver), trigram entity
resolution, weighted benchmark aggregation + uncertainty, blind-review Elo,
significance-gated rollout regressions, semver-pruned impact, automatic
change fan-out, watcher notifications, continuous-sync sweep, and the
real-provider OfferingExecutor.
"""

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.outbox import OutboxMessage
from app.controlplane.worker import HANDLERS, load_handlers
from app.ecosystem.models.catalog import AIModel, EntityAlias, ModelVersion
from app.ecosystem.models.graph import ImpactAnalysis
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.services.benchmark import BenchmarkService
from app.ecosystem.services.blind_review import BlindReviewService
from app.ecosystem.services.impact import ImpactService
from app.ecosystem.services.replacement import ReplacementService
from app.ecosystem.services.resolution import normalize_name, propose_resolution
from app.ecosystem.services.rollout import RolloutService
from app.ecosystem.services.stats import (
    bradley_terry,
    mean_ci95,
    pairwise_wins_from_scores,
    two_proportion_z_test,
    version_in_range,
    welch_t_test,
)
from app.ecosystem.services.sync import SyncService
from app.ecosystem.worker import sweep_due_sources
from tests.test_eco_services_db import (
    _catalog_payload,
    _fetcher_for,
    _mk_capability_tag,
    _mk_model_version,
    _mk_org,
    _mk_source,
    _mk_suite_with_cases,
    _mk_user,
)


@pytest.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


# ── Statistics kernel (pure) ────────────────────────────────────────


def test_welch_t_test_detects_and_ignores():
    clearly_different = welch_t_test([100, 101, 99, 100, 102] * 4, [200, 201, 199, 200, 198] * 4)
    assert clearly_different["p_value"] < 0.001
    noise = welch_t_test([100, 140, 80, 120, 95], [110, 90, 130, 85, 125])
    assert noise["p_value"] > 0.05
    assert welch_t_test([1.0], [2.0])["p_value"] == 1.0  # underpowered → never significant


def test_two_proportion_z():
    assert two_proportion_z_test(95, 100, 60, 100)["p_value"] < 0.001
    assert two_proportion_z_test(9, 10, 8, 10)["p_value"] > 0.05
    assert two_proportion_z_test(0, 0, 5, 10)["p_value"] == 1.0


def test_mean_ci95_shape():
    out = mean_ci95([1.0, 2.0, 3.0, 4.0, 5.0])
    assert out["n"] == 5 and out["mean"] == 3.0
    assert out["ci95"][0] < 3.0 < out["ci95"][1]
    degenerate = mean_ci95([7.0])
    assert degenerate["ci95"] == [7.0, 7.0]


def test_bradley_terry_orders_by_strength():
    # A beats B 9:1, B beats C 9:1, A beats C 10:0
    wins = {("A", "B"): 9.0, ("B", "A"): 1.0, ("B", "C"): 9.0, ("C", "B"): 1.0, ("A", "C"): 10.0}
    elo = bradley_terry(wins)
    assert elo["A"] > elo["B"] > elo["C"]
    assert bradley_terry({}) == {}


def test_pairwise_wins_from_scores_with_ties():
    rows = [
        {"context": "case1", "judge": "r1", "item": "run_a", "score": 5},
        {"context": "case1", "judge": "r1", "item": "run_b", "score": 3},
        {"context": "case1", "judge": "r2", "item": "run_a", "score": 4},
        {"context": "case1", "judge": "r2", "item": "run_b", "score": 4},
    ]
    wins = pairwise_wins_from_scores(rows)
    assert wins[("run_a", "run_b")] == 1.5  # one win + half a tie
    assert wins[("run_b", "run_a")] == 0.5


@pytest.mark.parametrize(
    "version,range_expr,expected",
    [
        ("2.0.0", ">=2.0 <3.0", True),
        ("3.0.0", ">=2.0 <3.0", False),
        ("v2.9.9", ">=2.0 <3.0", True),
        ("1.9", ">=2.0", False),
        ("1.4.2", "^1.2", True),
        ("2.0.0", "^1.2", False),
        ("1.2.9", "~1.2.3", True),
        ("1.3.0", "~1.2.3", False),
        ("2.1.0", "==2.1.0", True),
        ("2.1.0", "2.1.0", True),
        ("weird-version", ">=1.0", None),  # unparseable version → None (fail open)
        ("1.0.0", "banana", None),  # unparseable range → None
    ],
)
def test_version_in_range(version, range_expr, expected):
    assert version_in_range(version, range_expr) is expected


def test_normalize_name():
    assert normalize_name("GPT-Image_2  Pro!") == "gpt image 2 pro"
    assert normalize_name(None) is None
    assert normalize_name("###") is None


# ── Trigram entity resolution ───────────────────────────────────────


async def test_normalized_alias_auto_merges_despite_formatting_drift(db):
    source = await _mk_source(db)
    model = AIModel(canonical_name="ImageForge", slug=f"if-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    db.add(
        EntityAlias(
            entity_kind="model",
            entity_id=model.id,
            alias="image-forge-v2",
            alias_normalized=normalize_name("image-forge-v2"),
            alias_type="official_id",
        )
    )
    await db.flush()
    # Same identifier, different formatting: underscores + case drift
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model",
        external_ref="IMAGE_FORGE_V2", raw_hash="f" * 64,
        normalized={"official_id": "IMAGE_FORGE_V2", "name": "ImageForge"},
    )
    db.add(obs)
    await db.flush()
    candidate = await propose_resolution(db, obs)
    assert candidate.status == "auto_merged"
    assert obs.canonical_entity_id == model.id


async def test_trigram_similarity_finds_near_name(db):
    source = await _mk_source(db)
    unique = str(ULID()).lower()[-6:]
    model = AIModel(canonical_name=f"Photon Render {unique}", slug=f"pr-{unique}")
    db.add(model)
    await db.flush()
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model",
        external_ref=f"photon-renderer-{unique}", raw_hash="g" * 64,
        normalized={"name": f"Photon Renderer {unique}"},
    )
    db.add(obs)
    await db.flush()
    candidate = await propose_resolution(db, obs)
    # Indexed similarity finds it, but similarity NEVER auto-merges
    assert candidate.candidate_entity_id == model.id
    assert candidate.match_method == "similarity"
    assert candidate.status == "pending"
    assert 0 < float(candidate.confidence) <= 1


# ── Weighted aggregation + uncertainty ──────────────────────────────


async def test_dimension_stats_and_case_weights(db):
    admin = await _mk_user(db, "admin")
    svc = BenchmarkService(db)
    suite = await svc.create_suite(
        key=f"wsuite-{str(ULID()).lower()}", name="Weighted", family="ecommerce_hero",
        capability_key="image_generation", repeat_count=2, created_by=admin.id,
    )
    heavy = await svc.add_case(suite.id, name="heavy", prompt="p1", weight=3.0)
    await svc.add_case(suite.id, name="light", prompt="p2", weight=1.0)
    await svc.update_suite(suite.id, {"status": "active"})

    class SplitExecutor:
        async def execute_case(self, run, case, repeat):
            score = 1.0 if case.id == heavy.id else 0.0
            return {"output_assets": [], "latency_ms": 100, "usage": {},
                    "cost_usd": 0.01, "automated_scores": {"text_accuracy": score},
                    "failed": False, "retries": 0}

    bench = BenchmarkService(db, executor=SplitExecutor())
    run = await bench.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "W" * 26}
    )
    run = await bench.execute_run(run.id)
    # Weighted mean = (3*1 + 1*0)/4 = 0.75 — an unweighted mean would say 0.5
    assert run.dimension_scores["text_accuracy"] == 0.75
    stats = run.dimension_scores["dimension_stats"]
    assert stats["text_accuracy"]["n"] == 4
    assert stats["latency_ms"]["ci95"][0] <= stats["latency_ms"]["mean"]
    assert stats["reliability"]["n"] == 4


# ── Blind review → Bradley-Terry Elo ────────────────────────────────


async def test_reveal_computes_preference_elo(db):
    admin = await _mk_user(db, "admin")
    r1, r2 = await _mk_user(db), await _mk_user(db)
    suite = await _mk_suite_with_cases(db, admin, n_cases=1)
    bench = BenchmarkService(db)
    runs = []
    for _ in range(2):
        run = await bench.create_run(
            suite.id, target={"entity_kind": "model_version", "entity_id": str(ULID())}
        )
        runs.append(await bench.execute_run(run.id))
    blind = BlindReviewService(db)
    batch = await blind.create_batch(
        suite_id=suite.id, run_ids=[r.id for r in runs],
        reviewer_ids=[r1.id, r2.id], created_by=admin.id,
    )
    # Both reviewers consistently prefer runs[0]
    for reviewer in (r1, r2):
        for a in await blind.assignments_for(batch.id, reviewer.id):
            review = await db.get(
                __import__("app.ecosystem.models.benchmark", fromlist=["BenchmarkReview"]
                           ).BenchmarkReview, a["review_id"])
            preferred = review.run_id == runs[0].id
            await blind.submit(
                a["review_id"], reviewer_id=reviewer.id,
                scores={"quality": 5 if preferred else 2},
            )
    revealed = await blind.reveal(batch.id)
    elos = {r["run_id"]: r["dimension_scores"].get("human_pref_elo") for r in revealed["runs"]}
    assert elos[runs[0].id] is not None and elos[runs[1].id] is not None
    assert elos[runs[0].id] > elos[runs[1].id]


# ── Significance-gated rollout regression ───────────────────────────


class ListLatencyExecutor:
    """Fixed cost, latency drawn from a per-instance list (cycled)."""

    def __init__(self, latencies, cost=0.01):
        self.latencies = latencies
        self.cost = cost
        self.i = 0

    async def execute_case(self, run, case, repeat):
        latency = self.latencies[self.i % len(self.latencies)]
        self.i += 1
        return {"output_assets": [], "latency_ms": latency, "usage": {},
                "cost_usd": self.cost, "automated_scores": {},
                "failed": False, "retries": 0}


async def _rollout_with_latencies(db, admin, *, base_lat, cand_lat, thresholds):
    deprecated = await _mk_model_version(db, f"SOld{str(ULID())[-4:]}")
    candidate = await _mk_model_version(db, f"SNew{str(ULID())[-4:]}")
    suite = await _mk_suite_with_cases(db, admin, n_cases=3)  # 3 cases × 2 repeats = 6
    for target, lats in ((deprecated, base_lat), (candidate, cand_lat)):
        bench = BenchmarkService(db, executor=ListLatencyExecutor(lats))
        run = await bench.create_run(
            suite.id, target={"entity_kind": "model_version", "entity_id": target.id}
        )
        await bench.execute_run(run.id)
    ranked, _ = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    top = next(c for c in ranked if c.candidate_id == candidate.id)
    svc = RolloutService(db)
    plan = await svc.create(
        replacement_candidate_id=top.id, scope_type="benchmark_only",
        guardrails={"min_samples": 2, "thresholds": thresholds},
    )
    await svc.start(plan.id)
    return svc, await svc.evaluate(plan.id)


async def test_noisy_latency_difference_is_not_a_regression(db):
    admin = await _mk_user(db, "admin")
    # Slightly slower on average, hugely noisy → not significant → no block
    svc, plan = await _rollout_with_latencies(
        db, admin,
        base_lat=[100, 900, 200, 800, 150, 850],
        cand_lat=[120, 920, 230, 780, 170, 900],
        thresholds={"speed_p50_ms": 0},
    )
    entry = plan.comparison["speed_p50_ms"]
    assert entry["p_value"] > 0.05
    assert entry.get("regression") is False
    plan = await svc.decide(plan.id, decision="promote", actor_id=admin.id)
    assert plan.status == "promoted"


async def test_significant_latency_regression_blocks_promote(db):
    from app.exceptions import AppError

    admin = await _mk_user(db, "admin")
    svc, plan = await _rollout_with_latencies(
        db, admin,
        base_lat=[100, 102, 98, 101, 99, 100],
        cand_lat=[500, 505, 498, 502, 499, 501],
        thresholds={"speed_p50_ms": 50},
    )
    entry = plan.comparison["speed_p50_ms"]
    assert entry["p_value"] < 0.05 and entry["regression"] is True
    with pytest.raises(AppError) as exc:
        await svc.decide(plan.id, decision="promote", actor_id=admin.id)
    assert exc.value.code == "ECO_ROLLOUT_REGRESSION"


# ── Semver-pruned impact ────────────────────────────────────────────


async def test_impact_prunes_version_pinned_dependents(db):
    from app.ecosystem.services.graph import GraphService

    source = await _mk_source(db)
    model = AIModel(canonical_name=f"Pinned {ULID()}", slug=f"pin-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    version = ModelVersion(
        model_id=model.id, version="2.0.0", canonical_name="Pinned 2.0",
        lifecycle_status="verified",
    )
    db.add(version)
    await db.flush()
    graph = GraphService(db)
    affected_pack, safe_pack, unknown_pack = str(ULID()), str(ULID()), str(ULID())
    await graph.add_edge(from_kind="workflow_pack", from_id=affected_pack,
                         to_kind="model_version", to_id=version.id,
                         constraint_type="requires_model_version",
                         constraint_spec={"version_range": ">=2.0 <3.0"})
    await graph.add_edge(from_kind="workflow_pack", from_id=safe_pack,
                         to_kind="model_version", to_id=version.id,
                         constraint_type="requires_model_version",
                         constraint_spec={"version_range": ">=3.0"})
    await graph.add_edge(from_kind="workflow_pack", from_id=unknown_pack,
                         to_kind="model_version", to_id=version.id,
                         constraint_type="requires_model_version",
                         constraint_spec={"version_range": "not-a-range"})
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_deprecated",
        entity_kind="model_version", canonical_entity_kind="model_version",
        canonical_entity_id=version.id, raw_hash="s" * 64, normalized={},
    )
    db.add(obs)
    await db.flush()
    change = ChangeEvent(
        observation_id=obs.id, change_type="lifecycle", field="sunset_at",
        severity="sunset_risk", entity_kind="model_version",
        canonical_entity_id=version.id,
    )
    db.add(change)
    await db.flush()
    analysis = await ImpactService(db).compute(change.id)
    _, items = await ImpactService(db).get(analysis.id)
    affected_ids = {i.node_id for i in items}
    assert affected_pack in affected_ids
    assert unknown_pack in affected_ids  # unparseable range fails OPEN
    assert safe_pack not in affected_ids  # provably pinned elsewhere — pruned


# ── Automatic fan-out + watcher notifications ───────────────────────


async def test_change_event_fans_out_to_outbox_and_watchers(db):
    from app.ecosystem.services.watchlists import WatchlistService

    source = await _mk_source(db)
    model = AIModel(canonical_name=f"Fanout {ULID()}", slug=f"fan-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    ref = f"fanout-{str(ULID()).lower()}"
    db.add(EntityAlias(entity_kind="model", entity_id=model.id, alias=ref,
                       alias_normalized=normalize_name(ref), alias_type="official_id"))
    await db.flush()
    watcher = await _mk_user(db)
    watchlist = await WatchlistService(db).create(owner_id=watcher.id, name="fanout")
    await WatchlistService(db).add_item(
        watchlist.id, watcher.id, target_kind="model", target_id=model.id
    )
    # No "version" key: the adapter then classifies these as kind=model,
    # matching the alias we registered on the model entity
    v1 = _catalog_payload([{"id": ref, "name": "Fanout", "license": "research"}])
    v2 = _catalog_payload([{"id": ref, "name": "Fanout", "license": "commercial"}])
    await SyncService(db, fetcher=_fetcher_for(v1)).run_sync(source.id)
    await SyncService(db, fetcher=_fetcher_for(v2)).run_sync(source.id)
    # breaking license change on a resolved entity → both fan-out topics queued
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.canonical_entity_id == model.id,
            ChangeEvent.change_type == "license",
        )
    )
    assert change is not None and change.severity == "breaking"
    topics = [
        (m.topic, m.payload)
        for m in await db.scalars(
            select(OutboxMessage).where(OutboxMessage.status == "pending")
        )
        if m.payload.get("change_event_id") == change.id
    ]
    topic_names = {t for t, _ in topics}
    assert "eco.compute_impact" in topic_names
    assert "eco.notify_watchers" in topic_names

    # Drive the notify handler inline — idempotent across redelivery
    load_handlers()
    await HANDLERS["eco.notify_watchers"](db, {"change_event_id": change.id})
    await HANDLERS["eco.notify_watchers"](db, {"change_event_id": change.id})
    from app.models.notification import Notification

    notes = list(
        await db.scalars(
            select(Notification).where(
                Notification.user_id == watcher.id,
                Notification.type == "ecosystem_change",
            )
        )
    )
    assert len(notes) == 1
    assert notes[0].data["change_event_id"] == change.id
    # Impact handler consumes the queued analysis exactly once
    await HANDLERS["eco.compute_impact"](db, {"change_event_id": change.id})
    await HANDLERS["eco.compute_impact"](db, {"change_event_id": change.id})
    analyses = list(
        await db.scalars(
            select(ImpactAnalysis).where(ImpactAnalysis.change_event_id == change.id)
        )
    )
    assert len(analyses) == 1


async def test_price_change_magnitude_recorded(db):
    source = await _mk_source(db)
    ref = f"mag-{str(ULID()).lower()}"
    v1 = _catalog_payload(
        [{"id": ref, "name": "Mag", "version": "1",
          "pricing": [{"unit": "image", "price": 0.02, "currency": "USD"}]}]
    )
    v2 = _catalog_payload(
        [{"id": ref, "name": "Mag", "version": "1",
          "pricing": [{"unit": "image", "price": 0.03, "currency": "USD"}]}]
    )
    await SyncService(db, fetcher=_fetcher_for(v1)).run_sync(source.id)
    await SyncService(db, fetcher=_fetcher_for(v2)).run_sync(source.id)
    change = await db.scalar(
        select(ChangeEvent)
        .join(EcosystemObservation, ChangeEvent.observation_id == EcosystemObservation.id)
        .where(
            ChangeEvent.change_type == "price",
            EcosystemObservation.external_ref == ref,
        )
    )
    assert change is not None
    assert change.new_value["magnitude"]["change_pct"] == 50.0
    assert change.severity == "update_available"


# ── Continuous discovery sweep ──────────────────────────────────────


async def test_sweep_enqueues_only_due_sources(db):
    from datetime import UTC, datetime, timedelta

    due = await _mk_source(db, name=f"due-{ULID()}", sync_interval_minutes=30)
    due.last_sync_at = datetime.now(UTC) - timedelta(minutes=45)
    fresh = await _mk_source(db, name=f"fresh-{ULID()}", sync_interval_minutes=30)
    fresh.last_sync_at = datetime.now(UTC) - timedelta(minutes=5)
    never_synced = await _mk_source(db, name=f"never-{ULID()}")
    paused = await _mk_source(db, name=f"paused-{ULID()}")
    paused.status = "paused"
    await db.flush()
    await sweep_due_sources(db)
    queued_ids = {
        m.payload.get("source_id")
        for m in await db.scalars(
            select(OutboxMessage).where(
                OutboxMessage.topic == "eco.sync_source",
                OutboxMessage.status == "pending",
            )
        )
    }
    assert due.id in queued_ids
    assert never_synced.id in queued_ids
    assert fresh.id not in queued_ids
    assert paused.id not in queued_ids


# ── Real-provider OfferingExecutor ──────────────────────────────────


async def _mk_offering(db, *, active=True, connection_status="active"):
    from app.models.provider import ProviderAdapter, ProviderConnection, ProviderModelOffering

    adapter = await db.scalar(select(ProviderAdapter).where(ProviderAdapter.key == "mock"))
    if adapter is None:
        adapter = ProviderAdapter(key="mock", name="Mock")
        db.add(adapter)
        await db.flush()
    org = await _mk_org(db)
    connection = ProviderConnection(
        org_id=org.id, adapter_id=adapter.id, name="bench-conn", status=connection_status
    )
    db.add(connection)
    await db.flush()
    offering = ProviderModelOffering(
        connection_id=connection.id, capability_key="image_generation",
        model_name="mock-image-1", cost_per_call_usd=0.0123, is_active=active,
    )
    db.add(offering)
    await db.flush()
    return offering


async def test_offering_executor_runs_real_adapter_chain(db):
    admin = await _mk_user(db, "admin")
    await _mk_capability_tag(db)
    offering = await _mk_offering(db)
    version = await _mk_model_version(db, f"Real{str(ULID())[-4:]}")
    suite = await _mk_suite_with_cases(db, admin, n_cases=1)
    bench = BenchmarkService(db)  # executor=None → auto-select OfferingExecutor
    run = await bench.create_run(
        suite.id,
        target={
            "entity_kind": "model_version",
            "entity_id": version.id,
            "offering_id": offering.id,
        },
        triggered_by=admin.id,
    )
    assert run.environment_snapshot["executor"] == "OfferingExecutor"
    run = await bench.execute_run(run.id)
    assert run.status == "completed"
    results = await bench.list_results(run.id)
    assert len(results) == 2
    for result in results:
        assert result.failed is False
        assert result.output_assets[0]["kind"] == "provider_output"
        assert result.output_assets[0]["ref"].startswith("mock-asset-")
        assert float(result.cost_usd) == 0.0123
        assert result.usage["events"]  # metering events captured
        assert result.latency_ms is not None


async def test_offering_executor_inactive_connection_captured_as_failure(db):
    admin = await _mk_user(db, "admin")
    await _mk_capability_tag(db)
    offering = await _mk_offering(db, connection_status="paused")
    suite = await _mk_suite_with_cases(db, admin, n_cases=1)
    bench = BenchmarkService(db)
    run = await bench.create_run(
        suite.id,
        target={"entity_kind": "model_version", "entity_id": "X" * 26,
                "offering_id": offering.id},
    )
    run = await bench.execute_run(run.id)
    assert run.status == "completed"  # provider failure is DATA, not a crash
    results = await bench.list_results(run.id)
    assert all(r.failed for r in results)
    assert "BENCH_CONNECTION_INACTIVE" in (results[0].error or "")
    assert run.dimension_scores["reliability"] == 0.0
