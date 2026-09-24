"""Ecosystem service DB tests (ADR-016 Part T).

Covers: ingestion idempotency, ETag 304, size cap, timeout/retry, circuit
breaker, robots gate, rate limit, typed change detection, resolution
auto-merge policy + low-confidence blocking, source conflicts, lifecycle
state machine, evidence upgrade/downgrade, pricing reconciliation gate,
telemetry privacy thresholds, impact BFS w/ cycles, private edge isolation,
hard-incompatibility separation, draft publish gate, rollout gates, blind
review identity hiding, watchlist ownership.

Runs against the dev Postgres (eco01 applied); every test rolls back.
"""

import json
from datetime import UTC, datetime, timedelta

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.benchmark import BenchmarkSuite
from app.ecosystem.models.catalog import AIModel, EntityAlias, ModelVersion
from app.ecosystem.models.mapping import CapabilityMapping
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.models.source import EcosystemSource
from app.ecosystem.security import EcoSecurityError
from app.ecosystem.services.benchmark import BenchmarkService
from app.ecosystem.services.blind_review import BlindReviewService
from app.ecosystem.services.capability_mapping import CapabilityMappingService
from app.ecosystem.services.catalog import CatalogService, LifecycleService
from app.ecosystem.services.drafts import DraftService
from app.ecosystem.services.graph import GraphService
from app.ecosystem.services.impact import ImpactService
from app.ecosystem.services.pricing import PricingService
from app.ecosystem.services.replacement import ReplacementService
from app.ecosystem.services.resolution import ResolutionService, propose_resolution
from app.ecosystem.services.rollout import RolloutService
from app.ecosystem.services.sources import SourceService
from app.ecosystem.services.sync import FetchResult, SyncService
from app.ecosystem.services.telemetry import TelemetryService, aggregate_metrics
from app.ecosystem.services.watchlists import WatchlistService
from app.exceptions import AppError
from app.models.user import User


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def _catalog_payload(models: list[dict]) -> bytes:
    return json.dumps({"models": models}).encode()


def _fetcher_for(body: bytes, status: int = 200, etag: str | None = "W/\"abc\""):
    async def fetch(url, *, etag=None, last_modified=None, timeout, max_bytes):
        if status == 304:
            return FetchResult(304, b"")
        return FetchResult(200, body, etag="W/\"abc\"", last_modified="Mon, 01 Sep 2026")

    return fetch


async def _mk_source(db, **overrides) -> EcosystemSource:
    defaults = dict(
        name=f"src-{ULID()}",
        source_type="provider_api",
        trust_level="official",
        adapter_key="json_catalog",
        base_url="https://example.com/models",
    )
    defaults.update(overrides)
    return await SourceService(db).create(**defaults)


async def _mk_user(db, role="member") -> User:
    from app.models.user import UserRole, UserStatus

    user = User(
        email=f"eco-{ULID()}@test.local",
        display_name="Eco Tester",
        role=UserRole.ADMIN if role == "admin" else UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_org(db):
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization

    tenant = TenantAccount(name=f"eco-t-{ULID()}", slug=f"ecot-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(
        tenant_id=tenant.id, name=f"eco-org-{ULID()}", slug=f"eco-{str(ULID()).lower()}"
    )
    db.add(org)
    await db.flush()
    return org


# ── Part A: sources & sync ──────────────────────────────────────────


async def test_source_rejects_inline_credentials(db):
    with pytest.raises(AppError) as exc:
        await _mk_source(db, config={"api_key": "sk-live-123"})
    assert exc.value.code == "VALIDATION_ERROR"


async def test_source_rejects_private_base_url(db):
    with pytest.raises(EcoSecurityError):
        await _mk_source(db, base_url="https://192.168.0.1/feed")


async def test_sync_idempotent_on_same_payload(db):
    source = await _mk_source(db)
    body = _catalog_payload([{"id": "m-1", "name": "Gen", "version": "1.0"}])
    svc = SyncService(db, fetcher=_fetcher_for(body))
    run1 = await svc.run_sync(source.id)
    assert run1.status == "success"
    assert run1.observations_created == 1
    run2 = await svc.run_sync(source.id)
    assert run2.observations_created == 0  # duplicate raw_hash no-ops


async def test_sync_updates_etag_and_304_short_circuits(db):
    source = await _mk_source(db)
    body = _catalog_payload([{"id": "m-2", "name": "Gen2", "version": "1.0"}])
    await SyncService(db, fetcher=_fetcher_for(body)).run_sync(source.id)
    assert source.etag == 'W/"abc"'
    run = await SyncService(db, fetcher=_fetcher_for(b"", status=304)).run_sync(source.id)
    assert run.status == "not_modified"
    assert run.observations_created == 0


async def test_sync_size_cap_fails_run(db):
    source = await _mk_source(db)

    async def big_fetch(url, *, etag, last_modified, timeout, max_bytes):
        raise EcoSecurityError("ECO_PAYLOAD_TOO_LARGE", "too big", 413)

    with pytest.raises(EcoSecurityError):
        await SyncService(db, fetcher=big_fetch).run_sync(source.id)
    assert source.consecutive_failures == 1


async def test_sync_retries_then_fails_and_circuit_breaker_pauses(db):
    source = await _mk_source(db)
    calls = {"n": 0}

    async def flaky(url, *, etag, last_modified, timeout, max_bytes):
        calls["n"] += 1
        raise TimeoutError("connect timeout")

    for _ in range(5):
        with pytest.raises(AppError) as exc:
            await SyncService(db, fetcher=flaky).run_sync(source.id)
        assert exc.value.code == "ECO_FETCH_FAILED"
    assert calls["n"] == 15  # 3 attempts per sync
    assert source.status == "paused"  # circuit breaker at 5
    with pytest.raises(AppError) as exc:
        await SyncService(db, fetcher=flaky).run_sync(source.id)
    assert exc.value.code == "ECO_SOURCE_PAUSED"


async def test_sync_refuses_without_robots_attestation(db):
    source = await _mk_source(db, robots_compliant=False)
    with pytest.raises(AppError) as exc:
        await SyncService(db).run_sync(source.id)
    assert exc.value.code == "ECO_ROBOTS_NOT_ATTESTED"


async def test_sync_rate_limited(db):
    source = await _mk_source(db, rate_limit_per_hour=1)
    body = _catalog_payload([{"id": "m-rl", "name": "RL", "version": "1"}])
    await SyncService(db, fetcher=_fetcher_for(body)).run_sync(source.id)
    with pytest.raises(AppError) as exc:
        await SyncService(db, fetcher=_fetcher_for(body)).run_sync(source.id)
    assert exc.value.code == "ECO_RATE_LIMITED"


async def test_observation_parser_provenance_stamped(db):
    source = await _mk_source(db)
    body = _catalog_payload([{"id": "m-p", "name": "Prov", "version": "1"}])
    run = await SyncService(db, fetcher=_fetcher_for(body)).run_sync(source.id)
    from sqlalchemy import select

    obs = await db.scalar(
        select(EcosystemObservation).where(EcosystemObservation.sync_run_id == run.id)
    )
    assert obs.parser_version == source.parser_version
    assert obs.raw_hash
    assert obs.extraction_method == "structured"


# ── Part B: typed change detection ──────────────────────────────────


async def test_price_and_license_changes_are_typed(db):
    source = await _mk_source(db)
    v1 = _catalog_payload(
        [{"id": "m-c", "name": "C", "version": "1", "license": "research",
          "pricing": [{"unit": "image", "price": 0.02, "currency": "USD"}]}]
    )
    v2 = _catalog_payload(
        [{"id": "m-c", "name": "C", "version": "1", "license": "commercial",
          "pricing": [{"unit": "image", "price": 0.05, "currency": "USD"}]}]
    )
    await SyncService(db, fetcher=_fetcher_for(v1)).run_sync(source.id)
    run2 = await SyncService(db, fetcher=_fetcher_for(v2)).run_sync(source.id)
    assert run2.changes_detected >= 2
    from sqlalchemy import select

    changes = list(await db.scalars(select(ChangeEvent)))
    by_type = {c.change_type: c for c in changes if c.field in ("license", "pricing")}
    assert by_type["license"].severity == "breaking"
    assert by_type["license"].old_value == {"value": "research"}
    assert by_type["price"].severity == "update_available"  # price went up


async def test_security_advisory_creates_critical_change(db):
    source = await _mk_source(db, source_type="manual_analyst", adapter_key="manual",
                              base_url=None)
    payload = json.dumps(
        {"event_type": "security_advisory", "entity_kind": "node_package",
         "external_ref": "org/nodes", "normalized": {"advisory": "GHSA-1"}}
    ).encode()
    run = await SyncService(db).run_sync(source.id, raw_payload=payload)
    assert run.changes_detected == 1
    from sqlalchemy import select

    change = await db.scalar(
        select(ChangeEvent).where(ChangeEvent.change_type == "security")
    )
    assert change.severity == "security_critical"


# ── Part C: entity resolution ───────────────────────────────────────


async def test_official_id_alias_auto_merges(db):
    source = await _mk_source(db)
    model = AIModel(canonical_name="Gen3", slug=f"gen3-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    db.add(EntityAlias(entity_kind="model", entity_id=model.id,
                       alias="gen-3-official", alias_type="official_id"))
    await db.flush()
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model",
        external_ref="gen-3-official", raw_hash="h" * 64,
        normalized={"official_id": "gen-3-official", "name": "Gen3"},
    )
    db.add(obs)
    await db.flush()
    candidate = await propose_resolution(db, obs)
    assert candidate.status == "auto_merged"
    assert obs.canonical_entity_id == model.id


async def test_similarity_match_requires_human_confirmation(db):
    source = await _mk_source(db)
    model = AIModel(canonical_name="ImageGen Ultra", slug=f"igu-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model",
        external_ref="imagegen-ultra-x", raw_hash="i" * 64,
        normalized={"name": "ImageGen Ultra X"},
    )
    db.add(obs)
    await db.flush()
    candidate = await propose_resolution(db, obs)
    assert candidate.status == "pending"  # low-confidence merge BLOCKED
    assert candidate.match_method in ("similarity",)
    assert obs.canonical_entity_id is None
    # Human confirms
    admin = await _mk_user(db, "admin")
    confirmed, entity_id = await ResolutionService(db).confirm(
        candidate.id, actor_id=admin.id
    )
    assert confirmed.status == "confirmed"
    assert obs.canonical_entity_id == entity_id


async def test_resolution_creates_new_entity_when_no_match(db):
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model_version",
        external_ref="brand-new-model-1.0", raw_hash="n" * 64,
        normalized={"name": "Brand New Model", "version": "1.0",
                    "api_identifier": "bnm-1-0"},
    )
    db.add(obs)
    await db.flush()
    candidate = await propose_resolution(db, obs)
    assert candidate.candidate_entity_id is None
    admin = await _mk_user(db, "admin")
    _, entity_id = await ResolutionService(db).confirm(candidate.id, actor_id=admin.id)
    version = await db.get(ModelVersion, entity_id)
    assert version.version == "1.0"
    assert version.lifecycle_status == "discovered"
    # Aliases registered so the NEXT observation auto-merges
    obs2 = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model_version",
        external_ref="brand-new-model-1.0", raw_hash="n2" + "n" * 62,
        normalized={"name": "Brand New Model", "version": "1.0"},
    )
    db.add(obs2)
    await db.flush()
    candidate2 = await propose_resolution(db, obs2)
    assert candidate2.status == "auto_merged"


async def test_source_conflicts_surfaced_not_merged(db):
    s1 = await _mk_source(db, name=f"s1-{ULID()}")
    s2 = await _mk_source(db, name=f"s2-{ULID()}", trust_level="community")
    model = AIModel(canonical_name="Conflicted", slug=f"conf-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    for src, license_val, h in ((s1, "commercial", "a"), (s2, "research-only", "b")):
        db.add(EcosystemObservation(
            source_id=src.id, event_type="catalog_snapshot", entity_kind="model",
            canonical_entity_kind="model", canonical_entity_id=model.id,
            raw_hash=h * 64, normalized={"license": license_val},
        ))
    await db.flush()
    conflicts = await CatalogService(db).conflicting_observations("model", model.id)
    fields = {c["field"] for c in conflicts}
    assert "license" in fields  # both retained, conflict surfaced


# ── Part L: lifecycle state machine ─────────────────────────────────


async def test_lifecycle_valid_and_invalid_transitions(db):
    model = AIModel(canonical_name="LC", slug=f"lc-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    svc = LifecycleService(db)
    await svc.transition("model", model.id, to_status="under_review")
    await svc.transition("model", model.id, to_status="verified")
    with pytest.raises(AppError) as exc:  # verified -> retired is not legal
        await svc.transition("model", model.id, to_status="retired")
    assert exc.value.code == "ECO_INVALID_TRANSITION"
    with pytest.raises(AppError):  # deprecation needs a reason
        await svc.transition("model", model.id, to_status="deprecated")
    await svc.transition(
        "model", model.id, to_status="deprecated", reason="official_sunset"
    )
    history = await svc.history("model", model.id)
    assert [t.to_status for t in history] == ["under_review", "verified", "deprecated"]


# ── Part D: capability mapping evidence ─────────────────────────────


async def _mk_capability_tag(db, key="image_generation"):
    from sqlalchemy import select

    from app.models.capability import CapabilityTag

    tag = await db.scalar(select(CapabilityTag).where(CapabilityTag.key == key))
    if tag is None:
        tag = CapabilityTag(key=key, name=key, category="generation")
        db.add(tag)
        await db.flush()
    return tag


async def test_evidence_upgrade_ok_downgrade_blocked(db):
    await _mk_capability_tag(db)
    model = AIModel(canonical_name="Ev", slug=f"ev-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    svc = CapabilityMappingService(db)
    mapping = await svc.upsert(
        entity_kind="model", entity_id=model.id, capability_key="image_generation",
        evidence_level="vendor_claimed",
    )
    mapping = await svc.upsert(
        entity_kind="model", entity_id=model.id, capability_key="image_generation",
        evidence_level="benchmark_verified",
    )
    assert mapping.evidence_level == "benchmark_verified"
    with pytest.raises(AppError) as exc:
        await svc.upsert(
            entity_kind="model", entity_id=model.id, capability_key="image_generation",
            evidence_level="vendor_claimed",
        )
    assert exc.value.code == "ECO_EVIDENCE_DOWNGRADE"
    # force + admin allows the downgrade
    mapping = await svc.upsert(
        entity_kind="model", entity_id=model.id, capability_key="image_generation",
        evidence_level="vendor_claimed", force=True, actor_is_admin=True,
    )
    assert mapping.evidence_level == "vendor_claimed"


# ── Part E: pricing reconciliation gate ─────────────────────────────


async def test_pricing_approval_mints_cost_rate_never_auto(db):
    source = await _mk_source(db)
    model = AIModel(canonical_name="Priced", slug=f"pr-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    obs = EcosystemObservation(
        source_id=source.id, event_type="price_changed", entity_kind="model",
        canonical_entity_kind="model", canonical_entity_id=model.id,
        raw_hash="p" * 64,
        normalized={"pricing": [{"unit": "image", "price": 0.03, "currency": "USD"}]},
    )
    db.add(obs)
    await db.flush()
    svc = PricingService(db)
    rows = await svc.extract_from_observation(obs.id)
    assert len(rows) == 1
    row = rows[0]
    assert row.reconciliation_status == "unreviewed"
    assert row.approved_cost_rate_id is None  # nothing touched billing
    admin = await _mk_user(db, "admin")
    with pytest.raises(AppError):  # approve requires provider_key
        await svc.reconcile(row.id, decision="approve", actor_id=admin.id)
    row = await svc.reconcile(
        row.id, decision="approve", actor_id=admin.id,
        provider_key="mock", model_or_service="priced-model",
    )
    assert row.reconciliation_status == "approved"
    from app.controlplane.models.pricing import ProviderCostRate

    rate = await db.get(ProviderCostRate, row.approved_cost_rate_id)
    assert rate is not None and float(rate.unit_cost) == 0.03
    # Deciding twice is refused
    with pytest.raises(AppError) as exc:
        await svc.reconcile(row.id, decision="reject", actor_id=admin.id)
    assert exc.value.code == "ECO_INVALID_TRANSITION"


async def test_pricing_requires_resolved_entity(db):
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="price_changed", entity_kind="model",
        raw_hash="q" * 64,
        normalized={"pricing": [{"unit": "image", "price": 0.03}]},
    )
    db.add(obs)
    await db.flush()
    with pytest.raises(AppError) as exc:
        await PricingService(db).extract_from_observation(obs.id)
    assert exc.value.code == "ECO_MERGE_CONFIRMATION_REQUIRED"


# ── Part G: telemetry privacy thresholds ────────────────────────────


def test_aggregate_metrics_pure():
    rows = [
        {"succeeded": True, "retries": 0, "latency_ms": 100, "cost_usd": 0.1},
        {"succeeded": False, "retries": 2, "latency_ms": 900, "cost_usd": 0.2,
         "error_code": "provider_500"},
    ]
    m = aggregate_metrics(rows)
    assert m["success_rate"] == 0.5
    assert m["retry_rate"] == 1.0
    assert m["latency_p95_ms"] == 900
    assert m["error_distribution"] == {"provider_500": 1}


async def test_cross_tenant_snapshot_requires_thresholds(db):
    svc = TelemetryService(db)
    now = datetime.now(UTC)
    rows = [{"org_id": "o1", "succeeded": True, "retries": 0}] * 5
    with pytest.raises(AppError) as exc:
        await svc.write_snapshot(
            entity_kind="provider_offering", entity_id="X" * 26,
            window_start=now - timedelta(days=1), window_end=now,
            rows=rows, org_id=None,
        )
    assert exc.value.code == "ECO_TELEMETRY_THRESHOLD"
    # 20 samples from only 2 orgs — still blocked
    rows = [{"org_id": f"o{i % 2}", "succeeded": True} for i in range(20)]
    with pytest.raises(AppError):
        await svc.write_snapshot(
            entity_kind="provider_offering", entity_id="X" * 26,
            window_start=now - timedelta(days=1), window_end=now,
            rows=rows, org_id=None,
        )
    # 21 samples from 3 orgs — allowed
    rows = [{"org_id": f"o{i % 3}", "succeeded": True} for i in range(21)]
    snap = await svc.write_snapshot(
        entity_kind="provider_offering", entity_id="X" * 26,
        window_start=now - timedelta(days=1), window_end=now,
        rows=rows, org_id=None,
    )
    assert snap.sample_size == 21 and snap.org_id is None


# ── Part H/I: graph + impact ────────────────────────────────────────


async def test_impact_bfs_transitive_and_cycle_safe(db):
    source = await _mk_source(db)
    model = AIModel(canonical_name="Root", slug=f"root-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    graph = GraphService(db)
    ids = {k: str(ULID()) for k in "abcd"}
    # workflow_pack a -> model root; skill_pack b -> a; learning_path c -> b
    await graph.add_edge(from_kind="workflow_pack", from_id=ids["a"],
                         to_kind="model", to_id=model.id,
                         constraint_type="requires_model_version")
    await graph.add_edge(from_kind="skill_pack", from_id=ids["b"],
                         to_kind="workflow_pack", to_id=ids["a"])
    await graph.add_edge(from_kind="learning_path", from_id=ids["c"],
                         to_kind="skill_pack", to_id=ids["b"])
    # cycle: a depends on c's artifact somehow — must not loop
    await graph.add_edge(from_kind="workflow_pack", from_id=ids["a"],
                         to_kind="learning_path", to_id=ids["c"])
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_deprecated", entity_kind="model",
        canonical_entity_kind="model", canonical_entity_id=model.id,
        raw_hash="r" * 64, normalized={"sunset_at": "2026-12-31T00:00:00Z"},
    )
    db.add(obs)
    await db.flush()
    change = ChangeEvent(
        observation_id=obs.id, change_type="lifecycle", field="sunset_at",
        new_value={"sunset_at": "2026-12-31T00:00:00Z"}, severity="sunset_risk",
        entity_kind="model", canonical_entity_id=model.id,
    )
    db.add(change)
    await db.flush()
    analysis = await ImpactService(db).compute(change.id)
    assert analysis.classification == "sunset_risk"
    assert analysis.deadline_at is not None
    assert analysis.summary.get("workflow_pack") == 1
    assert analysis.summary.get("skill_pack") == 1
    assert analysis.summary.get("learning_path") == 1
    assert analysis.summary["truncated"] is False
    _, items = await ImpactService(db).get(analysis.id)
    depths = {i.node_kind: i.depth for i in items}
    assert depths["workflow_pack"] == 1
    assert depths["learning_path"] in (2, 3)
    assert all(i.recommended_action == "migrate" for i in items)


async def test_private_edges_isolated_by_org(db):
    org = await _mk_org(db)
    graph = GraphService(db)
    node = str(ULID())
    edge = await graph.add_edge(
        from_kind="workflow_pack", from_id=str(ULID()), to_kind="capability",
        to_id=node, constraint_type="requires_capability", org_id=org.id,
    )
    visible = await graph.edges_for_node("capability", node, org_id=org.id)
    assert len(visible["dependents"]) == 1
    hidden = await graph.edges_for_node("capability", node, org_id=None)
    assert len(hidden["dependents"]) == 0  # private edge never leaks
    with pytest.raises(AppError):  # removal outside the org: uniform 404
        await graph.remove_edge(edge.id, org_id="X" * 26)


# ── Part F: benchmark + blind review ────────────────────────────────


async def _mk_suite_with_cases(db, admin, n_cases=2) -> BenchmarkSuite:
    svc = BenchmarkService(db)
    suite = await svc.create_suite(
        key=f"suite-{str(ULID()).lower()}", name="Hero Suite", family="ecommerce_hero",
        capability_key="image_generation", budget_usd_cap=5.0, repeat_count=2,
        created_by=admin.id,
    )
    for i in range(n_cases):
        await svc.add_case(suite.id, name=f"case{i}", prompt=f"prompt {i}")
    await svc.update_suite(suite.id, {"status": "active"})
    return suite


async def test_benchmark_run_dimensions_and_budget(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin)
    svc = BenchmarkService(db)
    run = await svc.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "M" * 26},
        triggered_by=admin.id,
    )
    run = await svc.execute_run(run.id)
    assert run.status == "completed"
    dims = run.dimension_scores
    assert "reliability" in dims and "cost_per_case_usd" in dims and "speed_p50_ms" in dims
    assert "overall_score" not in dims  # never collapsed
    results = await svc.list_results(run.id)
    assert len(results) == 4  # 2 cases × 2 repeats
    assert float(run.total_cost_usd) > 0
    # Budget abort
    tiny = await svc.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "M" * 26},
        budget_usd_cap=0.005, triggered_by=admin.id,
    )
    tiny = await svc.execute_run(tiny.id)
    assert tiny.status == "failed"
    assert "ECO_BUDGET_EXCEEDED" in (tiny.error or "")


async def test_provider_failure_captured_not_fatal(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin, n_cases=1)

    class FailingExecutor:
        async def execute_case(self, run, case, repeat):
            if repeat == 0:
                raise RuntimeError("provider 500")
            return {"output_assets": [], "latency_ms": 100, "usage": {},
                    "cost_usd": 0.01, "automated_scores": {}, "failed": False,
                    "retries": 1}

    svc = BenchmarkService(db, executor=FailingExecutor())
    run = await svc.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "M" * 26}
    )
    run = await svc.execute_run(run.id)
    assert run.status == "completed"
    results = await svc.list_results(run.id)
    assert sum(1 for r in results if r.failed) == 1
    assert run.dimension_scores["reliability"] == 0.5


async def test_blind_review_hides_identity_until_all_submit(db):
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
    # Assignments never expose run identity
    assignments = await blind.assignments_for(batch.id, r1.id)
    assert assignments
    for a in assignments:
        assert "run_id" not in a and "target" not in a
        assert a["alias_label"].startswith("Model ")
    # Reveal refused while open
    with pytest.raises(AppError) as exc:
        await blind.reveal(batch.id)
    assert exc.value.code == "ECO_BLIND_REVIEW_SEALED"
    # Non-reviewer gets uniform 404
    outsider = await _mk_user(db)
    with pytest.raises(AppError):
        await blind.assignments_for(batch.id, outsider.id)
    # All submit → reveal allowed and human dims fold into run scores
    for reviewer in (r1, r2):
        for a in await blind.assignments_for(batch.id, reviewer.id):
            await blind.submit(a["review_id"], reviewer_id=reviewer.id,
                               scores={"quality": 4, "brief_adherence": 5})
    revealed = await blind.reveal(batch.id)
    assert {r["alias_label"] for r in revealed["runs"]} == {"Model A", "Model B"}
    run = await bench.get_run(runs[0].id)
    assert run.dimension_scores.get("quality") == 4.0


async def test_review_score_bounds(db):
    admin = await _mk_user(db, "admin")
    reviewer = await _mk_user(db)
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
        suite_id=suite.id, run_ids=[r.id for r in runs], reviewer_ids=[reviewer.id]
    )
    a = (await blind.assignments_for(batch.id, reviewer.id))[0]
    with pytest.raises(AppError):
        await blind.submit(a["review_id"], reviewer_id=reviewer.id, scores={"quality": 9})
    with pytest.raises(AppError):
        await blind.submit(a["review_id"], reviewer_id=reviewer.id, scores={})


# ── Part J: replacement ─────────────────────────────────────────────


async def _mk_model_version(db, name, *, commercial=True, lifecycle="verified",
                            model=None, caps=("image_generation",),
                            io=None) -> ModelVersion:
    if model is None:
        model = AIModel(canonical_name=name, slug=f"{name.lower()}-{str(ULID()).lower()}")
        db.add(model)
        await db.flush()
    version = ModelVersion(
        model_id=model.id, version="1.0", canonical_name=f"{name} 1.0",
        lifecycle_status=lifecycle, commercial_use_allowed=commercial,
    )
    db.add(version)
    await db.flush()
    await _mk_capability_tag(db)
    for cap in caps:
        await _mk_capability_tag(db, cap)
        db.add(CapabilityMapping(
            entity_kind="model_version", entity_id=version.id, capability_key=cap,
            evidence_level="benchmark_verified",
            io_spec=io or {"inputs": [{"type": "text"}], "outputs": [{"type": "image"}]},
        ))
    await db.flush()
    return version


async def test_replacement_hard_incompatible_separated(db):
    deprecated = await _mk_model_version(db, "OldGen")
    good = await _mk_model_version(db, "NewGen")
    # Bad candidate: missing output type => IO mismatch
    bad = await _mk_model_version(
        db, "BadGen",
        io={"inputs": [{"type": "text"}], "outputs": [{"type": "video"}]},
    )
    blocked = await _mk_model_version(db, "BlockedGen", lifecycle="blocked")
    svc = ReplacementService(db)
    ranked, incompatible = await svc.generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    ranked_ids = {c.candidate_id for c in ranked}
    incompatible_ids = {c.candidate_id for c in incompatible}
    assert good.id in ranked_ids
    assert bad.id in incompatible_ids and bad.id not in ranked_ids
    assert blocked.id in incompatible_ids
    # Explanation + breakdown present, weights normalized
    top = ranked[0]
    assert top.score_breakdown and top.explanation
    assert abs(sum(top.score_breakdown[k] * w for k, w in
                   __import__("app.ecosystem.models.replacement",
                              fromlist=["DEFAULT_REPLACEMENT_WEIGHTS"]
                              ).DEFAULT_REPLACEMENT_WEIGHTS.items()) - float(top.score)) < 0.01
    # Approving a hard-incompatible candidate is refused
    admin = await _mk_user(db, "admin")
    bad_candidate = next(c for c in incompatible if c.candidate_id == bad.id)
    with pytest.raises(AppError) as exc:
        await svc.decide(bad_candidate.id, decision="approve", actor_id=admin.id)
    assert exc.value.code == "ECO_HARD_INCOMPATIBLE"
    approved = await svc.decide(top.id, decision="approve", actor_id=admin.id)
    assert approved.status == "approved"


async def test_replacement_weight_validation(db):
    deprecated = await _mk_model_version(db, "WOld")
    svc = ReplacementService(db)
    with pytest.raises(AppError):
        await svc.generate_candidates(
            deprecated_kind="model_version", deprecated_id=deprecated.id,
            weights={"bogus": 1.0},
        )
    with pytest.raises(AppError):
        await svc.generate_candidates(
            deprecated_kind="model_version", deprecated_id=deprecated.id,
            weights={"cost": float("nan")},
        )


# ── Part K: drafts publish gate ─────────────────────────────────────


async def test_draft_cannot_skip_to_published(db):
    admin = await _mk_user(db, "admin")
    approver = await _mk_user(db, "admin")  # §17 four-eyes: approver ≠ creator
    svc = DraftService(db)
    draft = await svc.create(
        draft_type="skill_pack_update", title="Update",
        payload={"target_pack_id": "P" * 26, "suggestions": [{"kind": "lesson"}]},
        created_by=admin.id,
    )
    assert draft.status == "draft"
    with pytest.raises(AppError) as exc:  # draft -> published in one step
        await svc.transition(draft.id, to_status="published", actor_id=admin.id)
    assert exc.value.code == "ECO_DRAFT_NOT_APPROVED"
    await svc.transition(draft.id, to_status="in_review", actor_id=admin.id)
    with pytest.raises(AppError):  # in_review -> published also refused
        await svc.transition(draft.id, to_status="published", actor_id=approver.id)
    await svc.transition(draft.id, to_status="approved", actor_id=approver.id)
    draft = await svc.transition(draft.id, to_status="published", actor_id=approver.id)
    assert draft.status == "published"


async def test_invalid_draft_cannot_publish(db):
    admin = await _mk_user(db, "admin")
    approver = await _mk_user(db, "admin")  # §17 four-eyes
    svc = DraftService(db)
    draft = await svc.create(
        draft_type="workflow_pack", title="Broken", payload={"definition": {}},
        created_by=admin.id,
    )
    assert draft.validation["valid"] is False
    await svc.transition(draft.id, to_status="in_review", actor_id=admin.id)
    await svc.transition(draft.id, to_status="approved", actor_id=approver.id)
    with pytest.raises(AppError) as exc:
        await svc.transition(draft.id, to_status="published", actor_id=approver.id)
    assert exc.value.code == "ECO_DRAFT_NOT_APPROVED"


async def test_org_scoped_draft_uniform_404(db):
    org = await _mk_org(db)
    admin = await _mk_user(db, "admin")
    draft = await DraftService(db).create(
        draft_type="skill_pack_update", title="Private",
        payload={"target_pack_id": "P" * 26, "suggestions": [{}]},
        org_id=org.id, created_by=admin.id,
    )
    with pytest.raises(AppError) as exc:
        await DraftService(db).get(draft.id, org_id="Z" * 26)
    assert exc.value.status_code == 404  # not 403 — no existence oracle


# ── Part M: rollout gates ───────────────────────────────────────────


async def test_rollout_state_machine_and_promote_gate(db):
    admin = await _mk_user(db, "admin")
    deprecated = await _mk_model_version(db, "RolloutOld")
    await _mk_model_version(db, "RolloutNew")
    ranked, _ = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    candidate = ranked[0]
    svc = RolloutService(db)
    with pytest.raises(AppError):  # non-benchmark scope needs scope_ref
        await svc.create(replacement_candidate_id=candidate.id,
                         scope_type="selected_cohort")
    plan = await svc.create(replacement_candidate_id=candidate.id,
                            scope_type="benchmark_only")
    with pytest.raises(AppError) as exc:  # cannot promote before evaluation
        await svc.decide(plan.id, decision="promote", actor_id=admin.id)
    assert exc.value.code == "ECO_ROLLOUT_NOT_EVALUATED"
    await svc.start(plan.id)
    plan = await svc.evaluate(plan.id)
    assert plan.status == "evaluating"
    plan = await svc.decide(plan.id, decision="promote", actor_id=admin.id)
    assert plan.status == "promoted"
    # Promotion recorded a replacement edge — no bindings rewritten
    from sqlalchemy import select

    from app.ecosystem.models.replacement import ReplacementEdge

    edge = await db.scalar(select(ReplacementEdge).where(
        ReplacementEdge.from_id == deprecated.id,
        ReplacementEdge.edge_type == "recommended_replacement",
    ))
    assert edge is not None
    # Terminal states are frozen
    with pytest.raises(AppError):
        await svc.decide(plan.id, decision="reject", actor_id=admin.id)


async def test_rollout_refuses_hard_incompatible_candidate(db):
    deprecated = await _mk_model_version(db, "HIOld")
    await _mk_model_version(
        db, "HIBad",
        io={"inputs": [{"type": "text"}], "outputs": [{"type": "video"}]},
    )
    _, incompatible = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    with pytest.raises(AppError) as exc:
        await RolloutService(db).create(
            replacement_candidate_id=incompatible[0].id, scope_type="benchmark_only"
        )
    assert exc.value.code == "ECO_HARD_INCOMPATIBLE"


# ── Part P: watchlists ownership ────────────────────────────────────


async def test_watchlist_ownership_uniform_404(db):
    owner, other = await _mk_user(db), await _mk_user(db)
    svc = WatchlistService(db)
    watchlist = await svc.create(owner_id=owner.id, name="My watches")
    await svc.add_item(watchlist.id, owner.id, target_kind="provider",
                       target_id="P" * 26)
    with pytest.raises(AppError) as exc:
        await svc.list_items(watchlist.id, other.id)
    assert exc.value.status_code == 404
    # Duplicate add is a no-op returning the same row
    a = await svc.add_item(watchlist.id, owner.id, target_kind="provider",
                           target_id="P" * 26)
    b = await svc.add_item(watchlist.id, owner.id, target_kind="provider",
                           target_id="P" * 26)
    assert a.id == b.id

async def test_retired_entities_never_recommended(db):
    deprecated = await _mk_model_version(db, "RetOld")
    retired = await _mk_model_version(db, "RetGone", lifecycle="retired")
    good = await _mk_model_version(db, "RetNew")
    ranked, incompatible = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    all_ids = {c.candidate_id for c in ranked} | {c.candidate_id for c in incompatible}
    assert good.id in {c.candidate_id for c in ranked}
    # Retired is history — appears in NEITHER channel
    assert retired.id not in all_ids

async def test_merge_repoints_change_history_and_pending_resolutions(db):
    from app.ecosystem.models.catalog import ResolutionCandidate
    from app.ecosystem.models.observation import ChangeEvent
    from app.ecosystem.services.catalog import CatalogService

    admin = await _mk_user(db, "admin")
    tag = str(ULID()).lower()[:6]
    dup = AIModel(canonical_name=f"HistDup-{tag}", slug=f"hd-{tag}")
    survivor = AIModel(canonical_name=f"HistSurv-{tag}", slug=f"hs-{tag}")
    db.add_all([dup, survivor])
    await db.flush()
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="pricing_changed",
        canonical_entity_kind="model", canonical_entity_id=dup.id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
    )
    db.add(obs)
    await db.flush()
    change = ChangeEvent(
        observation_id=obs.id, change_type="price", field="pricing",
        severity="info", entity_kind="model", canonical_entity_id=dup.id,
    )
    pending = ResolutionCandidate(
        observation_id=obs.id, entity_kind="model",
        candidate_entity_id=dup.id, match_method="similarity",
        confidence=0.5, status="pending",
    )
    decided = ResolutionCandidate(
        observation_id=obs.id, entity_kind="model",
        candidate_entity_id=dup.id, match_method="similarity",
        confidence=0.5, status="confirmed",
    )
    db.add_all([change, pending, decided])
    await db.flush()

    await CatalogService(db).merge_entities("model", dup.id, survivor.id, actor_id=admin.id)
    await db.refresh(change)
    await db.refresh(pending)
    await db.refresh(decided)
    assert change.canonical_entity_id == survivor.id  # history follows survivor
    assert pending.candidate_entity_id == survivor.id  # pending re-pointed
    assert decided.candidate_entity_id == dup.id  # decided rows are history


async def test_rollout_refuses_stale_retired_candidate(db):
    from app.ecosystem.services.rollout import RolloutService

    deprecated = await _mk_model_version(db, "StaleOld")
    candidate_entity = await _mk_model_version(db, "StaleNew")
    ranked, _ = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    top = next(c for c in ranked if c.candidate_id == candidate_entity.id)
    # Entity gets retired AFTER the candidate row was generated
    candidate_entity.lifecycle_status = "retired"
    await db.flush()
    with pytest.raises(AppError) as exc:
        await RolloutService(db).create(
            replacement_candidate_id=top.id, scope_type="benchmark_only"
        )
    assert exc.value.code == "ECO_INVALID_TRANSITION"

async def test_rollout_min_samples_guardrail_blocks_promote(db):
    """Mutation-audit killer: with min_samples above the collected sample
    count, promote must refuse with ECO_ROLLOUT_INSUFFICIENT_SAMPLES."""
    admin = await _mk_user(db, "admin")
    deprecated = await _mk_model_version(db, "MinSampOld")
    await _mk_model_version(db, "MinSampNew")
    ranked, _ = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    svc = RolloutService(db)
    plan = await svc.create(
        replacement_candidate_id=ranked[0].id, scope_type="benchmark_only",
        guardrails={"min_samples": 999, "thresholds": {}},
    )
    await svc.start(plan.id)
    await svc.evaluate(plan.id)
    with pytest.raises(AppError) as exc:
        await svc.decide(plan.id, decision="promote", actor_id=admin.id)
    assert exc.value.code == "ECO_ROLLOUT_INSUFFICIENT_SAMPLES"

def test_auto_merge_policy_constants_are_pinned():
    """Mutation-audit pin: the auto-merge safety posture is a CONTRACT.
    similarity and llm_suggested must never auto-merge; the confidence floor
    must stay at 0.9; the LLM confidence cap must sit BELOW the floor so an
    LLM suggestion can never clear it even if the method set drifts."""
    from app.ecosystem.models.catalog import (
        AUTO_MERGE_METHODS,
        AUTO_MERGE_MIN_CONFIDENCE,
    )
    from app.ecosystem.services.llm_extraction import LLM_CONFIDENCE_CAP

    assert frozenset({"official_id", "alias"}) == AUTO_MERGE_METHODS
    assert AUTO_MERGE_MIN_CONFIDENCE == 0.9
    assert LLM_CONFIDENCE_CAP < AUTO_MERGE_MIN_CONFIDENCE


async def test_identical_name_similarity_still_needs_human(db):
    """Behavioural killer: even a PERFECT similarity score (identical name,
    passing any confidence floor) must queue for human confirmation — only
    deterministic identifiers auto-merge. Also pins that the recorded
    confidence is the real similarity, never inflated to 1.0."""
    source = await _mk_source(db)
    name = f"ExactTwin-{str(ULID()).lower()[:6]}"
    model = AIModel(canonical_name=name, slug=f"et-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model",
        external_ref=name.lower(), raw_hash=(str(ULID()).lower() * 3)[:64],
        normalized={"name": name},
    )
    db.add(obs)
    await db.flush()
    candidate = await propose_resolution(db, obs)
    assert candidate.match_method == "similarity"
    assert candidate.status == "pending"  # perfect similarity ≠ auto-merge
    assert obs.canonical_entity_id is None
    assert float(candidate.confidence) >= 0.9  # it DID clear the floor

async def test_resolution_confidence_values_are_exact(db):
    """Mutation-audit killer: recorded confidences are calibrated constants —
    alias hits are exactly 0.95 and a no-match candidate is exactly 0.0
    (an inflated constant would lie to the reviewer queue)."""
    source = await _mk_source(db)
    tag = str(ULID()).lower()[:6]
    model = AIModel(canonical_name=f"AliasCal-{tag}", slug=f"ac-{tag}")
    db.add(model)
    await db.flush()
    db.add(EntityAlias(entity_kind="model", entity_id=model.id,
                       alias=f"Alias Cal {tag}", alias_type="name"))
    await db.flush()
    obs_alias = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model",
        external_ref=f"zz-ext-{tag}", raw_hash=(str(ULID()).lower() * 3)[:64],
        normalized={"name": f"Alias Cal {tag}"},
    )
    db.add(obs_alias)
    await db.flush()
    cand_alias = await propose_resolution(db, obs_alias)
    # A curated alias is a deterministic identifier: exact normalized hit is
    # method "alias" at exactly 0.95 and AUTO-MERGES (aliases are human-entered
    # facts, unlike raw similarity which always queues)
    assert cand_alias.match_method == "alias"
    assert float(cand_alias.confidence) == 0.95
    assert cand_alias.status == "auto_merged"

    obs_none = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model",
        external_ref=f"zz-nomatch-{tag}", raw_hash=(str(ULID()).lower() * 3)[:64],
        normalized={"name": f"Zz Totally Unrelated {tag}"},
    )
    db.add(obs_none)
    await db.flush()
    cand_none = await propose_resolution(db, obs_none)
    assert cand_none.candidate_entity_id is None
    assert float(cand_none.confidence) == 0.0

async def test_review_submit_ownership_and_immutability(db):
    """Mutation-audit killers: (a) reviewer A cannot submit reviewer B's
    assignment (uniform 404, no oracle); (b) a submitted review is immutable —
    resubmission is refused, so scores can't be edited after (or near) reveal."""
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
    a1 = (await blind.assignments_for(batch.id, r1.id))[0]

    # (a) cross-reviewer submit → uniform 404
    with pytest.raises(AppError) as exc:
        await blind.submit(a1["review_id"], reviewer_id=r2.id, scores={"quality": 3})
    assert exc.value.status_code == 404

    # legitimate submit succeeds once...
    await blind.submit(a1["review_id"], reviewer_id=r1.id, scores={"quality": 4})
    # ...(b) and never twice — submitted scores are frozen
    with pytest.raises(AppError) as exc:
        await blind.submit(a1["review_id"], reviewer_id=r1.id, scores={"quality": 1})
    assert exc.value.code == "ECO_INVALID_TRANSITION"

async def test_capability_evidence_gates_and_curation_hygiene(db):
    """Mutation-audit killers ×3: (a) force WITHOUT admin cannot downgrade
    evidence; (b) an unknown evidence level is a 422, never a KeyError-500;
    (c) curated conflict values are sanitized (NUL would 500 at JSONB)."""
    from app.ecosystem.services.capability_mapping import CapabilityMappingService
    from app.ecosystem.services.catalog import CatalogService

    admin = await _mk_user(db, "admin")
    version = await _mk_model_version(db, "EvGate")
    svc = CapabilityMappingService(db)
    await _mk_capability_tag(db, "video_generation")
    await svc.upsert(
        entity_kind="model_version", entity_id=version.id,
        capability_key="video_generation", evidence_level="benchmark_verified",
        io_spec={"inputs": [{"type": "text"}], "outputs": [{"type": "video"}]},
        actor_id=admin.id,
    )
    # (a) downgrade with force but WITHOUT admin → refused
    with pytest.raises(AppError):
        await svc.upsert(
            entity_kind="model_version", entity_id=version.id,
            capability_key="video_generation", evidence_level="vendor_claimed",
            io_spec={"inputs": [{"type": "text"}], "outputs": [{"type": "video"}]},
            actor_id=admin.id, force=True, actor_is_admin=False,
        )
    # (b) unknown evidence level → clean 422
    with pytest.raises(AppError) as exc:
        await svc.upsert(
            entity_kind="model_version", entity_id=version.id,
            capability_key="video_generation", evidence_level="totally_made_up",
            io_spec={}, actor_id=admin.id,
        )
    assert exc.value.code == "VALIDATION_ERROR"
    # (c) curated value with a NUL byte is stored sanitized
    curated = await CatalogService(db).resolve_conflict(
        "model_version", version.id, field="license",
        chosen_value="MIT\x00 injected", actor_id=admin.id,
    )
    assert "\x00" not in curated["value"]  # NUL screened before JSONB

async def test_hard_compatibility_gate_covers_all_axes(db):
    """Mutation-audit killers ×4: missing capability, input-direction,
    non-commercial license and the license score direction are each hard
    gates — none may silently pass."""
    deprecated = await _mk_model_version(
        db, "AxesOld",
        caps=("image_generation", "video_generation"),
        io={"inputs": [{"type": "text"}, {"type": "image"}],
            "outputs": [{"type": "image"}]},
    )
    # Missing one required capability
    lacks_cap = await _mk_model_version(
        db, "AxesNoCap", caps=("image_generation",),
        io={"inputs": [{"type": "text"}, {"type": "image"}],
            "outputs": [{"type": "image"}]},
    )
    # Same capabilities but can't accept the image input
    lacks_input = await _mk_model_version(
        db, "AxesNoImgIn",
        caps=("image_generation", "video_generation"),
        io={"inputs": [{"type": "text"}], "outputs": [{"type": "image"}]},
    )
    # Non-commercial license
    non_commercial = await _mk_model_version(
        db, "AxesNoncom", commercial=False,
        caps=("image_generation", "video_generation"),
        io={"inputs": [{"type": "text"}, {"type": "image"}],
            "outputs": [{"type": "image"}]},
    )
    # Fully compatible control
    good = await _mk_model_version(
        db, "AxesGood",
        caps=("image_generation", "video_generation"),
        io={"inputs": [{"type": "text"}, {"type": "image"}],
            "outputs": [{"type": "image"}]},
    )

    ranked, incompatible = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id, limit=50
    )
    ranked_ids = {c.candidate_id for c in ranked}
    bad = {c.candidate_id: c for c in incompatible}

    assert good.id in ranked_ids

    def codes(c):
        return {f["code"] for f in (c.hard_failures or [])}

    assert lacks_cap.id in bad and "CAPABILITY_MISSING" in codes(bad[lacks_cap.id])
    assert lacks_input.id in bad and "IO_TYPE_MISMATCH" in codes(bad[lacks_input.id])
    assert non_commercial.id in bad and "LICENSE_INCOMPATIBLE" in codes(bad[non_commercial.id])
    # License score direction: commercial 1.0, non-commercial 0.0
    good_row = next(c for c in ranked if c.candidate_id == good.id)
    assert good_row.score_breakdown["license"] == 1.0
    assert bad[non_commercial.id].score_breakdown["license"] == 0.0

async def test_signals_expose_only_approved_verified_evidence(db):
    """Mutation-audit killers ×4: the matching/workforce signal surface is a
    DATA CONTRACT — only verified/recommended entities with evidence >=
    benchmark_verified appear; badges never come from vendor claims."""
    from app.ecosystem.models.mapping import CapabilityMapping
    from app.ecosystem.services.signals import SignalsService

    await _mk_capability_tag(db, "signal_gen")
    approved = await _mk_model_version(db, "SigOK", caps=())
    unapproved = await _mk_model_version(db, "SigNew", lifecycle="discovered", caps=())
    weak_evidence = await _mk_model_version(db, "SigWeak", caps=())
    db.add_all([
        CapabilityMapping(
            entity_kind="model_version", entity_id=approved.id,
            capability_key="signal_gen", evidence_level="benchmark_verified",
            io_spec={},
        ),
        CapabilityMapping(
            entity_kind="model_version", entity_id=unapproved.id,
            capability_key="signal_gen", evidence_level="benchmark_verified",
            io_spec={},
        ),
        CapabilityMapping(
            entity_kind="model_version", entity_id=weak_evidence.id,
            capability_key="signal_gen", evidence_level="vendor_claimed",
            io_spec={},
        ),
    ])
    await db.flush()

    svc = SignalsService(db)
    rows = await svc.matching_signals(capability_key="signal_gen")
    ids = {r["entity_id"] for r in rows}
    assert approved.id in ids
    assert unapproved.id not in ids       # lifecycle gate
    assert weak_evidence.id not in ids    # evidence floor

    badges = await svc.registry_badges(entity_refs=[
        ("model_version", approved.id),
        ("model_version", weak_evidence.id),
    ])
    assert "benchmark_verified" in badges[f"model_version:{approved.id}"]
    assert "benchmark_verified" not in badges.get(
        f"model_version:{weak_evidence.id}", []
    )  # vendor claims never badge

async def test_sync_release_edges_from_manifest_definition(db):
    """Regression + mutation killers ×4: sync-release reads the definition
    from the MANIFEST (the model has no .definition — the old attribute
    access 500'd on every real release), dedupes capabilities, skips
    non-string entries, and emits requires_capability edges from the
    workflow_pack_release kind."""
    import hashlib
    import json as _json

    from sqlalchemy import select as _select

    from app.ecosystem.models.graph import DependencyEdge
    from app.ecosystem.services.graph import GraphService
    from app.models.skill_pack import PackStatus, PackVisibility
    from app.models.workflow_pack import WorkflowPack, WorkflowPackRelease

    org = await _mk_org(db)
    pack = WorkflowPack(
        owner_org_id=org.id, name="EdgePack",
        slug=f"edgepack-{str(ULID()).lower()}",
        status=PackStatus.DRAFT, visibility=PackVisibility.PRIVATE,
    )
    db.add(pack)
    await db.flush()
    manifest = {
        "schema_version": 1,
        "version": "1.0.0",
        "name": "EdgePack",
        "definition": {"steps": [
            {"id": "s1", "capability": "image_generation"},
            {"id": "s2", "capability": "image_generation"},  # duplicate → one edge
            {"id": "s3", "capability": 123},                  # non-string → skipped
            {"id": "s4", "capability": "video_generation"},
        ]},
    }
    release = WorkflowPackRelease(
        pack_id=pack.id, version="1.0.0", manifest=manifest,
        checksum=hashlib.sha256(_json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
        step_count=4,
    )
    db.add(release)
    await db.flush()

    created = await GraphService(db).sync_release_edges(release.id)
    assert created == 2  # dedup + non-string skip
    edges = list(await db.scalars(
        _select(DependencyEdge).where(DependencyEdge.from_id == release.id)
    ))
    assert len(edges) == 2
    for edge in edges:
        assert edge.from_kind == "workflow_pack_release"
        assert edge.constraint_type == "requires_capability"
    assert {e.constraint_spec["capability_key"] for e in edges} == {
        "image_generation", "video_generation",
    }

async def test_search_wildcards_are_literal(db):
    """Round-83 killer: LIKE wildcards in user search text are LITERAL —
    searching "%" must not match everything, and "50%_off" matches only the
    entity actually named that way."""
    from app.ecosystem.services.catalog import CatalogService

    tag = str(ULID()).lower()[:6]
    weird = AIModel(canonical_name=f"50%_off-{tag}", slug=f"wo-{tag}")
    plain = AIModel(canonical_name=f"PlainGen-{tag}", slug=f"pl-{tag}")
    db.add_all([weird, plain])
    await db.flush()
    svc = CatalogService(db)

    rows, _total = await svc.list_entities("model", search=f"50%_off-{tag}", limit=50)
    assert {r.id for r in rows} == {weird.id}
    # "%" is a literal percent sign, not match-all
    rows, _total = await svc.list_entities("model", search=f"%_off-{tag}", limit=50)
    assert {r.id for r in rows} == {weird.id}  # literal '%' and '_' both
    rows, _total = await svc.list_entities("model", search=f"PlainGen-{tag}", limit=50)
    assert {r.id for r in rows} == {plain.id}
    rows, _total = await svc.list_entities("model", search=f"_off-{tag}", limit=50)
    assert {r.id for r in rows} == {weird.id}  # '_' literal too


def test_escape_like_helper():
    from app.ecosystem.security import escape_like

    assert escape_like("50%_off") == "50\\%\\_off"
    assert escape_like("a\\b") == "a\\\\b"

def test_normalize_name_bounds_and_strictness():
    """Round-84 killers: the resolution key is BOUNDED (300 chars — an
    unbounded key defeats the alias index) and STRICT (non-strings are None,
    never coerced — str(dict) garbage keys would auto-merge junk)."""
    from app.ecosystem.services.resolution import normalize_name

    assert normalize_name("A" * 1000) == "a" * 300  # capped, casefolded
    assert normalize_name(12345) is None            # never coerced
    assert normalize_name({"name": "x"}) is None
    assert normalize_name(None) is None
    assert normalize_name("GPT-Image 2") == normalize_name("gpt_image_2")

async def test_source_update_guards(db):
    """Round-86 killers ×3: updating base_url re-runs the SSRF validator
    (an internal URL must be refused); an adapter swap re-stamps
    parser_version (§11.5); re-activating resets the circuit breaker."""
    from app.ecosystem.services.adapters import ADAPTERS
    from app.ecosystem.services.sources import SourceService

    source = await _mk_source(db, adapter_key="manual")
    source.consecutive_failures = 7
    await db.flush()
    svc = SourceService(db)

    # SSRF re-check on update
    with pytest.raises(Exception) as exc:
        await svc.update(source.id, {"base_url": "http://localhost/feed"})
    assert "SSRF" in str(exc.value) or "ECO_SSRF" in str(getattr(exc.value, "code", ""))

    # Adapter swap re-stamps parser version (start from a stale stamp so
    # the re-stamp is observable even when adapter versions coincide)
    source.parser_version = "0.1-stale"
    await db.flush()
    await svc.update(source.id, {"adapter_key": "huggingface"})
    assert source.parser_version == ADAPTERS["huggingface"].version
    assert source.parser_version != "0.1-stale"

    # Un-pausing resets the breaker
    await svc.update(source.id, {"status": "paused"})
    source.consecutive_failures = 7
    await db.flush()
    await svc.update(source.id, {"status": "active"})
    assert source.consecutive_failures == 0


async def test_conflicts_need_two_values_and_use_latest_per_source(db):
    """Round-86 killers ×2: a field every source agrees on is NOT a conflict,
    and each source is represented by its LATEST observation (an updated
    source that now agrees must clear the conflict)."""
    from app.ecosystem.services.catalog import CatalogService

    tag = str(ULID()).lower()[:6]
    model = AIModel(canonical_name=f"ConfGen-{tag}", slug=f"cf-{tag}")
    db.add(model)
    await db.flush()
    s1, s2 = await _mk_source(db), await _mk_source(db)

    def obs(source, license_val, days_ago):
        return EcosystemObservation(
            source_id=source.id, event_type="catalog_snapshot",
            canonical_entity_kind="model", canonical_entity_id=model.id,
            raw_hash=(str(ULID()).lower() * 3)[:64],
            normalized={"license": license_val},
            observed_at=datetime.now(UTC) - timedelta(days=days_ago),
        )

    # s1 said GPL long ago, then corrected itself to MIT; s2 says MIT
    db.add_all([obs(s1, "GPL", 10), obs(s1, "MIT", 1), obs(s2, "MIT", 2)])
    await db.flush()
    conflicts = await CatalogService(db).conflicting_observations("model", model.id)
    licenses = [c for c in conflicts if c["field"] == "license"]
    # Latest-per-source: both sources NOW say MIT → agreement, no conflict
    assert licenses == []

async def test_price_extraction_bounds(db):
    """Round-87 killers ×4: extraction drops negative prices, absurd prices
    (>1e9), unknown units — and caps currency to 3 chars — while keeping the
    one valid entry."""
    from app.ecosystem.services.pricing import PricingService

    tag = str(ULID()).lower()[:6]
    model = AIModel(canonical_name=f"XGen-{tag}", slug=f"xg-{tag}")
    db.add(model)
    await db.flush()
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="pricing_changed",
        canonical_entity_kind="model", canonical_entity_id=model.id,
        raw_hash=(str(ULID()).lower() * 3)[:64],
        normalized={"pricing": [
            {"unit": "image", "price": -5},              # negative → dropped
            {"unit": "image", "price": 2e9},             # absurd → dropped
            {"unit": "gpu_hour", "price": 1.0},          # unknown unit → dropped
            {"unit": "image", "price": 0.04, "currency": "dollars"},  # kept, capped
        ]},
    )
    db.add(obs)
    await db.flush()
    rows = await PricingService(db).extract_from_observation(obs.id)
    assert len(rows) == 1
    assert float(rows[0].price) == 0.04
    assert rows[0].currency == "DOL"  # capped to 3 chars, uppercased

async def test_rollout_decide_note_sanitized_and_terminal_states_frozen(db):
    """Round-89 killers: the operator note is screened (NUL would 500 at the
    column) and terminal states refuse further decisions including abort."""
    admin = await _mk_user(db, "admin")
    deprecated = await _mk_model_version(db, "NoteOld")
    await _mk_model_version(db, "NoteNew")
    ranked, _ = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    svc = RolloutService(db)
    plan = await svc.create(
        replacement_candidate_id=ranked[0].id, scope_type="benchmark_only"
    )
    await svc.start(plan.id)
    await svc.evaluate(plan.id)
    plan = await svc.decide(
        plan.id, decision="reject", actor_id=admin.id, note="bad\x00actor\x01note"
    )
    assert plan.status == "rejected"
    assert "\x00" not in (plan.note or "") and "\x01" not in (plan.note or "")
    assert "badactor" in (plan.note or "").replace(" ", "")
    # Terminal: even abort is refused
    with pytest.raises(AppError):
        await svc.decide(plan.id, decision="abort", actor_id=admin.id)

async def test_review_comment_is_screened(db):
    """Round-90 killer: reviewer comments are sanitized — NUL bytes must not
    reach the column (R87 class)."""
    admin = await _mk_user(db, "admin")
    r1 = await _mk_user(db)
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
        reviewer_ids=[r1.id], created_by=admin.id,
    )
    a1 = (await blind.assignments_for(batch.id, r1.id))[0]
    review = await blind.submit(
        a1["review_id"], reviewer_id=r1.id,
        scores={"quality": 4}, comment="good\x00but\x02odd",
    )
    assert "\x00" not in (review.comment or "")
    assert "\x02" not in (review.comment or "")
    assert "good" in (review.comment or "")

async def test_catalog_update_screens_and_bounds_inputs(db):
    """Round-91 killers: PATCHed catalog fields are screened (NUL) and
    bounded (alias list capped at 50, each alias 300 chars, external_ids
    capped at 50 keys)."""
    from app.ecosystem.services.catalog import CatalogService

    tag = str(ULID()).lower()[:6]
    model = AIModel(canonical_name=f"UpGen-{tag}", slug=f"up-{tag}")
    db.add(model)
    await db.flush()
    entity = await CatalogService(db).update(
        "model", model.id,
        {
            "canonical_name": "Clean\x00Name",
            "aliases": [f"a{i}\x00x" for i in range(80)],
            "external_ids": {f"k{i}": "v\x00v" for i in range(80)},
        },
    )
    assert "\x00" not in entity.canonical_name
    assert len(entity.aliases) <= 50
    assert all("\x00" not in a for a in entity.aliases)
    assert len(entity.external_ids) <= 50
    assert all("\x00" not in (v or "") for v in entity.external_ids.values())
