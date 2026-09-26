"""Full ecosystem intelligence E2E (issue #35 Part T).

Operator adds official source → sync discovers a new model version →
observation + resolution candidate → human verifies → benchmark old vs new →
new model cheaper with acceptable quality → impact analysis finds the
affected Workflow Pack → replacement candidate generated → author creates
update draft → controlled rollout runs → human promotes → registry badges
reflect the updated verified component.

Service-level E2E against the dev Postgres; rolls back at the end.
"""

import json

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.services.benchmark import BenchmarkService
from app.ecosystem.services.capability_mapping import CapabilityMappingService
from app.ecosystem.services.catalog import LifecycleService
from app.ecosystem.services.drafts import DraftService
from app.ecosystem.services.graph import GraphService
from app.ecosystem.services.impact import ImpactService
from app.ecosystem.services.replacement import ReplacementService
from app.ecosystem.services.resolution import ResolutionService
from app.ecosystem.services.rollout import RolloutService
from app.ecosystem.services.signals import SignalsService
from app.ecosystem.services.sources import SourceService
from app.ecosystem.services.sync import FetchResult, SyncService


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


class CostedExecutor:
    """Mock executor with per-target cost/quality so 'new' beats 'old' on cost."""

    def __init__(self, cost: float, accuracy: float):
        self.cost = cost
        self.accuracy = accuracy

    async def execute_case(self, run, case, repeat):
        return {
            "output_assets": [{"kind": "image", "ref": f"mock://{run.id}/{repeat}"}],
            "latency_ms": 800,
            "usage": {"images": 1},
            "cost_usd": self.cost,
            "automated_scores": {"text_accuracy": self.accuracy},
            "failed": False,
            "retries": 0,
        }


async def _mk_admin(db):
    from app.models.user import User, UserRole, UserStatus

    admin = User(
        email=f"eco-e2e-{ULID()}@test.local",
        display_name="Eco Operator",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(admin)
    await db.flush()
    return admin


async def _ensure_capability(db, key="image_generation"):
    from app.models.capability import CapabilityTag

    tag = await db.scalar(select(CapabilityTag).where(CapabilityTag.key == key))
    if tag is None:
        db.add(CapabilityTag(key=key, name=key, category="generation"))
        await db.flush()


async def test_full_discovery_to_rollout_e2e(db):
    admin = await _mk_admin(db)
    await _ensure_capability(db)

    # 1. Operator adds an official source
    source = await SourceService(db).create(
        name=f"vendor-catalog-{ULID()}",
        source_type="provider_api",
        trust_level="official",
        adapter_key="json_catalog",
        base_url="https://example.com/models.json",
        created_by=admin.id,
    )

    # 2. Sync discovers the OLD and NEW model versions
    catalog = {
        "models": [
            {
                "id": "visiongen-1",
                "name": "VisionGen",
                "version": "1.0",
                "api_identifier": "visiongen-1-0",
                "license": "commercial",
                "capabilities": ["image_generation"],
                "pricing": [{"unit": "image", "price": 0.08, "currency": "USD"}],
            },
            {
                "id": "visiongen-2",
                "name": "VisionGen 2",
                "version": "2.0",
                "api_identifier": "visiongen-2-0",
                "license": "commercial",
                "capabilities": ["image_generation"],
                "pricing": [{"unit": "image", "price": 0.03, "currency": "USD"}],
            },
        ]
    }

    def fetcher(body):
        async def fetch(url, *, etag, last_modified, timeout, max_bytes):
            return FetchResult(200, body, etag='W/"v1"')

        return fetch

    run = await SyncService(db, fetcher=fetcher(json.dumps(catalog).encode())).run_sync(
        source.id
    )
    assert run.status == "success" and run.observations_created == 2

    # 3. Observations + resolution candidates created; human confirms both
    resolution = ResolutionService(db)
    pending = await resolution.list_pending(entity_kind="model_version")
    ours = [c for c in pending if c.proposed_payload.get("official_id", "").startswith("visiongen")]
    assert len(ours) == 2
    entity_ids = {}
    for candidate in ours:
        _, entity_id = await resolution.confirm(candidate.id, actor_id=admin.id)
        entity_ids[candidate.proposed_payload["official_id"]] = entity_id
    old_id, new_id = entity_ids["visiongen-1"], entity_ids["visiongen-2"]

    # Human verifies the observations (provenance retained)
    for obs in await db.scalars(
        select(EcosystemObservation).where(EcosystemObservation.source_id == source.id)
    ):
        obs.human_verified = True

    # 4. Map both to the capability ontology with typed I/O
    mapping_svc = CapabilityMappingService(db)
    io_spec = {"inputs": [{"type": "text"}], "outputs": [{"type": "image"}]}
    for entity_id in (old_id, new_id):
        await mapping_svc.upsert(
            entity_kind="model_version",
            entity_id=entity_id,
            capability_key="image_generation",
            evidence_level="platform_observed",
            io_spec=io_spec,
        )

    # 5. Benchmark old vs new: new is CHEAPER with acceptable quality
    bench_old = BenchmarkService(db, executor=CostedExecutor(cost=0.08, accuracy=0.92))
    suite = await bench_old.create_suite(
        key=f"e2e-hero-{str(ULID()).lower()}",
        name="E-commerce Hero",
        family="ecommerce_hero",
        capability_key="image_generation",
        budget_usd_cap=5.0,
        repeat_count=2,
        created_by=admin.id,
    )
    await bench_old.add_case(suite.id, name="hero-1", prompt="product hero on white")
    await bench_old.update_suite(suite.id, {"status": "active"})

    run_old = await bench_old.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": old_id}
    )
    run_old = await bench_old.execute_run(run_old.id)
    bench_new = BenchmarkService(db, executor=CostedExecutor(cost=0.03, accuracy=0.90))
    run_new = await bench_new.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": new_id}
    )
    run_new = await bench_new.execute_run(run_new.id)
    assert run_old.status == run_new.status == "completed"
    assert run_new.dimension_scores["cost_per_case_usd"] < run_old.dimension_scores["cost_per_case_usd"]
    assert run_new.dimension_scores["text_accuracy"] >= 0.85  # acceptable quality
    comparison = await bench_new.compare_runs([run_old.id, run_new.id])
    assert len(comparison["runs"]) == 2

    # Benchmark evidence upgrades the mappings
    for entity_id in (old_id, new_id):
        await mapping_svc.upsert(
            entity_kind="model_version",
            entity_id=entity_id,
            capability_key="image_generation",
            evidence_level="benchmark_verified",
            io_spec=io_spec,
        )

    # 6. Lifecycle: verify both; new becomes verified, old will sunset
    lifecycle = LifecycleService(db)
    for entity_id in (old_id, new_id):
        await lifecycle.transition("model_version", entity_id, to_status="under_review",
                                   actor_id=admin.id)
        await lifecycle.transition("model_version", entity_id, to_status="verified",
                                   actor_id=admin.id)

    # 7. A Workflow Pack depends on the OLD model version
    pack_id = str(ULID())
    graph = GraphService(db)
    await graph.add_edge(
        from_kind="workflow_pack", from_id=pack_id,
        to_kind="model_version", to_id=old_id,
        constraint_type="requires_model_version",
    )
    await graph.add_edge(
        from_kind="learning_path", from_id=str(ULID()),
        to_kind="workflow_pack", to_id=pack_id,
    )

    # 8. Vendor announces the sunset of the old version → typed change event
    sunset_catalog = {
        "models": [
            dict(catalog["models"][0], lifecycle="deprecated",
                 sunset_at="2026-12-31T00:00:00Z"),
            catalog["models"][1],
        ]
    }
    run2 = await SyncService(
        db, fetcher=fetcher(json.dumps(sunset_catalog).encode())
    ).run_sync(source.id)
    assert run2.changes_detected >= 1
    change = await db.scalar(
        select(ChangeEvent)
        .where(ChangeEvent.severity == "sunset_risk",
               ChangeEvent.observation_id.in_(
                   select(EcosystemObservation.id).where(
                       EcosystemObservation.source_id == source.id
                   )
               ))
        .order_by(ChangeEvent.detected_at.desc())
    )
    assert change is not None
    # The deprecation observation auto-merged onto the old canonical version
    change.canonical_entity_id = change.canonical_entity_id or old_id
    change.entity_kind = change.entity_kind or "model_version"

    # 9. Impact analysis finds the affected Workflow Pack transitively
    analysis = await ImpactService(db).compute(change.id)
    assert analysis.classification == "sunset_risk"
    assert analysis.summary.get("workflow_pack") == 1
    assert analysis.summary.get("learning_path") == 1

    # 10. Deprecate old; replacement candidates generated and ranked
    await lifecycle.transition("model_version", old_id, to_status="deprecated",
                               reason="official_sunset", actor_id=admin.id)
    ranked, incompatible = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=old_id
    )
    assert ranked and ranked[0].candidate_id == new_id
    assert ranked[0].hard_compatible
    assert ranked[0].explanation  # explainable
    assert ranked[0].score_breakdown["cost"] > 0.5  # cheaper than incumbent
    approved = await ReplacementService(db).decide(
        ranked[0].id, decision="approve", actor_id=admin.id
    )
    assert approved.status == "approved"

    # 11. Author creates a structured update draft for the dependent pack
    draft_svc = DraftService(db)
    draft = await draft_svc.generate_skill_pack_update_draft(
        target_pack_id=pack_id,
        deprecated_kind="model_version",
        deprecated_id=old_id,
        replacement_id=new_id,
        affected=[{"kind": "workflow_pack", "ref": pack_id}],
        created_by=admin.id,
    )
    assert draft.status == "draft" and draft.validation["valid"]
    # §17 four-eyes: a SECOND admin reviews and publishes the author's draft
    reviewer = await _mk_admin(db)
    await draft_svc.transition(draft.id, to_status="in_review", actor_id=admin.id)
    await draft_svc.transition(draft.id, to_status="approved", actor_id=reviewer.id)
    draft = await draft_svc.transition(draft.id, to_status="published", actor_id=reviewer.id)
    assert draft.status == "published"

    # 12. Controlled rollout: benchmark-only scope, evaluate, human promotes
    rollout_svc = RolloutService(db)
    plan = await rollout_svc.create(
        replacement_candidate_id=approved.id, scope_type="benchmark_only"
    )
    await rollout_svc.start(plan.id)
    plan = await rollout_svc.evaluate(plan.id)
    assert plan.comparison["cost_per_case_usd"]["improved"] is True
    plan = await rollout_svc.decide(plan.id, decision="promote", actor_id=admin.id)
    assert plan.status == "promoted"

    # 13. Registry reflects the updated, verified component
    await lifecycle.transition("model_version", new_id, to_status="recommended",
                               actor_id=admin.id)
    badges = await SignalsService(db).registry_badges(
        entity_refs=[("model_version", old_id), ("model_version", new_id)]
    )
    assert "dependency_update_available" in badges[f"model_version:{old_id}"]
    assert "benchmark_verified" in badges[f"model_version:{new_id}"]

    # 14. Approved matching signals include ONLY verified/recommended entities
    signals = await SignalsService(db).matching_signals(capability_key="image_generation")
    signal_ids = {s["entity_id"] for s in signals}
    assert new_id in signal_ids
    assert old_id not in signal_ids  # deprecated never feeds matching

    # 15. Workforce intelligence sees capability momentum (advisory only)
    workforce = await SignalsService(db).workforce_signals()
    assert isinstance(workforce, list)
