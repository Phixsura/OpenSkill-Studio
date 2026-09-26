"""Platform-maturity round tests (ADR-016 §13).

ETag conditional GET, cursor pagination, iCal deprecation feed, webhook
fan-out for org watchlists, canonical entity merge, catalog export,
inter-rater agreement, suite snapshot drift gate, source health.
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.worker import HANDLERS, load_handlers
from app.ecosystem.models.catalog import EntityAlias, ModelVersion
from app.ecosystem.models.graph import DependencyEdge
from app.ecosystem.models.mapping import CapabilityMapping
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.models.replacement import ReplacementEdge
from app.ecosystem.services.benchmark import BenchmarkService
from app.ecosystem.services.catalog import CatalogService, LifecycleService
from app.ecosystem.services.resolution import normalize_name
from app.ecosystem.services.sources import SourceService
from app.ecosystem.services.stats import cohen_kappa, reviewer_agreement
from app.ecosystem.services.sync import SyncService
from app.ecosystem.services.watchlists import WatchlistService
from app.exceptions import AppError
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


# ── Inter-rater agreement (pure) ────────────────────────────────────


def test_cohen_kappa_perfect_and_chance():
    assert cohen_kappa(["a", "b", "a", "b"], ["a", "b", "a", "b"]) == 1.0
    # Systematic disagreement → kappa below zero
    assert cohen_kappa(["a", "a", "b", "b"], ["b", "b", "a", "a"]) < 0
    assert cohen_kappa([], []) is None
    assert cohen_kappa(["a", "a"], ["a", "a"]) == 1.0  # degenerate single category


def test_reviewer_agreement_shapes():
    rows = [
        {"context": "c1", "judge": "r1", "item": "A", "score": 5},
        {"context": "c1", "judge": "r1", "item": "B", "score": 2},
        {"context": "c1", "judge": "r2", "item": "A", "score": 4},
        {"context": "c1", "judge": "r2", "item": "B", "score": 1},
        {"context": "c2", "judge": "r1", "item": "A", "score": 3},
        {"context": "c2", "judge": "r1", "item": "B", "score": 4},
        {"context": "c2", "judge": "r2", "item": "A", "score": 5},
        {"context": "c2", "judge": "r2", "item": "B", "score": 2},
    ]
    out = reviewer_agreement(rows)
    assert out["reviewer_pairs"] == 1
    assert out["percent_agreement"] == 0.5  # agree on c1, disagree on c2
    assert out["mean_cohen_kappa"] is not None


# ── Cursor pagination ───────────────────────────────────────────────


async def test_observation_cursor_pagination(db):
    source = await _mk_source(db)
    for i in range(5):
        db.add(
            EcosystemObservation(
                source_id=source.id, event_type="catalog_snapshot",
                raw_hash=f"{i}" * 64, normalized={"i": i},
            )
        )
    await db.flush()
    # Emulate the endpoint's cursor walk at page size 2
    async def page(cursor):
        query = select(EcosystemObservation).where(EcosystemObservation.source_id == source.id)
        if cursor:
            query = query.where(EcosystemObservation.id < cursor)
        rows = list(await db.scalars(query.order_by(EcosystemObservation.id.desc()).limit(3)))
        has_more = len(rows) > 2
        rows = rows[:2]
        return rows, (rows[-1].id if has_more and rows else None)

    seen: list[str] = []
    cursor = None
    for _ in range(4):
        rows, cursor = await page(cursor)
        seen += [r.id for r in rows]
        if cursor is None:
            break
    assert len(seen) == 5
    assert len(set(seen)) == 5  # no duplicates, no gaps
    assert seen == sorted(seen, reverse=True)  # ULID time-desc order


# ── Canonical entity merge ──────────────────────────────────────────


async def test_merge_entities_repoints_everything_and_audits(db):
    await _mk_capability_tag(db)
    admin = await _mk_user(db, "admin")
    source = await _mk_source(db)
    dup = await _mk_model_version(db, f"Dup{str(ULID())[-4:]}")
    survivor = await _mk_model_version(db, f"Srv{str(ULID())[-4:]}")
    # Observation, alias, dependency edge, price obs pointing at the duplicate
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_released", entity_kind="model_version",
        canonical_entity_kind="model_version", canonical_entity_id=dup.id,
        raw_hash="m" * 64, normalized={},
    )
    db.add(obs)
    db.add(EntityAlias(entity_kind="model_version", entity_id=dup.id,
                       alias=f"dup-alias-{ULID()}", alias_normalized="dup alias",
                       alias_type="official_id"))
    pack_id = str(ULID())
    db.add(DependencyEdge(from_kind="workflow_pack", from_id=pack_id,
                          to_kind="model_version", to_id=dup.id,
                          constraint_type="requires_model_version"))
    await db.flush()

    svc = CatalogService(db)
    with pytest.raises(AppError):
        await svc.merge_entities("model_version", dup.id, dup.id, actor_id=admin.id)
    outcome = await svc.merge_entities("model_version", dup.id, survivor.id, actor_id=admin.id)
    assert outcome["merged_into"] == survivor.id
    assert outcome["moved"]["observations"] == 1
    assert outcome["moved"]["edges"] == 1
    # References re-pointed
    await db.refresh(obs)
    assert obs.canonical_entity_id == survivor.id
    edge = await db.scalar(select(DependencyEdge).where(DependencyEdge.from_id == pack_id))
    assert edge.to_id == survivor.id
    # Duplicate retired + supersedes audit edge; mapping conflict kept higher evidence
    await db.refresh(dup)
    assert dup.lifecycle_status == "retired"
    supersedes = await db.scalar(
        select(ReplacementEdge).where(
            ReplacementEdge.from_id == dup.id, ReplacementEdge.edge_type == "supersedes"
        )
    )
    assert supersedes is not None and supersedes.to_id == survivor.id
    # Capability mapping merged (both had image_generation from _mk_model_version):
    mappings = list(
        await db.scalars(
            select(CapabilityMapping).where(
                CapabilityMapping.entity_kind == "model_version",
                CapabilityMapping.entity_id == survivor.id,
            )
        )
    )
    assert len(mappings) == 1
    dup_mappings = list(
        await db.scalars(
            select(CapabilityMapping).where(CapabilityMapping.entity_id == dup.id)
        )
    )
    assert dup_mappings == []


# ── Suite snapshot drift gate ───────────────────────────────────────


async def test_suite_drift_invalidates_queued_run(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin, n_cases=1)
    bench = BenchmarkService(db)
    run = await bench.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "D" * 26}
    )
    snapshot = run.environment_snapshot["suite_snapshot"]
    assert snapshot["case_count"] == 1 and snapshot["cases_fingerprint"]
    # Suite edited between queue and execute → run refuses to measure drift
    await bench.add_case(suite.id, name="sneaky-extra", prompt="added later")
    run = await bench.execute_run(run.id)
    assert run.status == "failed"
    assert "ECO_SUITE_DRIFT" in run.error
    # A fresh run against the edited suite works
    run2 = await bench.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "D" * 26}
    )
    run2 = await bench.execute_run(run2.id)
    assert run2.status == "completed"


# ── Source health ───────────────────────────────────────────────────


async def test_source_health_summary(db):
    source = await _mk_source(db)
    ok = _catalog_payload([{"id": f"h-{ULID()}", "name": "H", "version": "1"}])
    await SyncService(db, fetcher=_fetcher_for(ok)).run_sync(source.id)

    async def boom(url, *, etag, last_modified, timeout, max_bytes):
        raise TimeoutError("flaky")

    with pytest.raises(AppError):
        await SyncService(db, fetcher=boom).run_sync(source.id)
    health = await SourceService(db).health(source.id)
    assert health["runs"] == 2
    assert health["by_status"]["success"] == 1
    assert health["by_status"]["failed"] == 1
    assert health["success_rate"] == 0.5
    assert health["observations_created"] == 1
    assert "flaky" in health["last_error"]


# ── Webhook fan-out for org watchlists ──────────────────────────────


async def test_org_watchlist_triggers_ecosystem_webhook(db, monkeypatch):
    from app.ecosystem.models.catalog import AIModel
    from app.services import webhook as webhook_module

    delivered: list[tuple[str, str, dict]] = []

    async def fake_trigger(self, org_id, event_type, payload):
        delivered.append((org_id, event_type, payload))

    monkeypatch.setattr(webhook_module.WebhookService, "trigger_event", fake_trigger)

    source = await _mk_source(db)
    org = await _mk_org(db)
    watcher = await _mk_user(db)
    model = AIModel(canonical_name=f"WH {ULID()}", slug=f"wh-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    ref = f"wh-{str(ULID()).lower()}"
    db.add(EntityAlias(entity_kind="model", entity_id=model.id, alias=ref,
                       alias_normalized=normalize_name(ref), alias_type="official_id"))
    await db.flush()
    wl_svc = WatchlistService(db)
    watchlist = await wl_svc.create(owner_id=watcher.id, name="org-watch", org_id=org.id)
    await wl_svc.add_item(watchlist.id, watcher.id, target_kind="model", target_id=model.id)

    v1 = _catalog_payload([{"id": ref, "name": "WH", "license": "research"}])
    v2 = _catalog_payload([{"id": ref, "name": "WH", "license": "commercial"}])
    await SyncService(db, fetcher=_fetcher_for(v1)).run_sync(source.id)
    await SyncService(db, fetcher=_fetcher_for(v2)).run_sync(source.id)
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.canonical_entity_id == model.id,
            ChangeEvent.change_type == "license",
        )
    )
    load_handlers()
    await HANDLERS["eco.notify_watchers"](db, {"change_event_id": change.id})
    assert len(delivered) == 1
    org_id, event_type, payload = delivered[0]
    assert org_id == org.id
    assert event_type == "ecosystem.change"
    assert payload["change_event_id"] == change.id
    assert payload["severity"] == "breaking"


def test_ecosystem_change_is_a_valid_webhook_event():
    from app.services.webhook import VALID_EVENT_TYPES

    assert "ecosystem.change" in VALID_EVENT_TYPES


# ── iCal + export shape (service-level) ─────────────────────────────


async def test_upcoming_sunsets_feed_ical_source(db):
    model_version = await _mk_model_version(db, f"Ical{str(ULID())[-4:]}")
    row = await db.get(ModelVersion, model_version.id)
    row.sunset_at = datetime.now(UTC) + timedelta(days=30)
    await db.flush()
    sunsets = await LifecycleService(db).upcoming_sunsets(within_days=90)
    ours = [s for s in sunsets if s["entity_id"] == model_version.id]
    assert ours and ours[0]["sunset_at"] is not None

async def test_muted_org_watchlist_suppresses_webhook(db, monkeypatch):
    """Round-119 killer: §24 noise controls apply to ORG webhook fan-out too —
    a muted (or below-threshold) org watchlist must not fire the webhook."""
    from datetime import UTC, datetime, timedelta

    from app.ecosystem.models.catalog import AIModel
    from app.services import webhook as webhook_module

    delivered: list[tuple[str, str, dict]] = []

    async def fake_trigger(self, org_id, event_type, payload):
        delivered.append((org_id, event_type, payload))

    monkeypatch.setattr(webhook_module.WebhookService, "trigger_event", fake_trigger)

    source = await _mk_source(db)
    muted_org = await _mk_org(db)
    strict_org = await _mk_org(db)
    watcher = await _mk_user(db)
    model = AIModel(canonical_name=f"WHm {ULID()}", slug=f"whm-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    ref = f"whm-{str(ULID()).lower()}"
    db.add(EntityAlias(entity_kind="model", entity_id=model.id, alias=ref,
                       alias_normalized=normalize_name(ref), alias_type="official_id"))
    await db.flush()
    wl_svc = WatchlistService(db)
    muted_wl = await wl_svc.create(owner_id=watcher.id, name="muted-org", org_id=muted_org.id)
    await wl_svc.add_item(muted_wl.id, watcher.id, target_kind="model", target_id=model.id)
    await wl_svc.update_settings(
        muted_wl.id, watcher.id,
        muted_until=datetime.now(UTC) + timedelta(days=1),
    )
    strict_wl = await wl_svc.create(owner_id=watcher.id, name="strict-org", org_id=strict_org.id)
    await wl_svc.add_item(strict_wl.id, watcher.id, target_kind="model", target_id=model.id)
    await wl_svc.update_settings(strict_wl.id, watcher.id, min_severity="security_critical")

    v1 = _catalog_payload([{"id": ref, "name": "WHm", "license": "research"}])
    v2 = _catalog_payload([{"id": ref, "name": "WHm", "license": "commercial"}])
    await SyncService(db, fetcher=_fetcher_for(v1)).run_sync(source.id)
    await SyncService(db, fetcher=_fetcher_for(v2)).run_sync(source.id)
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.canonical_entity_id == model.id,
            ChangeEvent.change_type == "license",
        )
    )
    load_handlers()
    await HANDLERS["eco.notify_watchers"](db, {"change_event_id": change.id})
    # breaking < security_critical, and the other list is muted → NO webhooks
    fired_orgs = [d[0] for d in delivered]
    assert muted_org.id not in fired_orgs
    assert strict_org.id not in fired_orgs

async def test_changes_cursor_pagination_is_complete_and_duplicate_free(db):
    """Round-193 killer: walking the change feed by cursor yields every row
    exactly once (no skips at page boundaries, no repeats) — the property
    that makes delta consumers trustworthy."""
    from app.ecosystem.models.catalog import AIModel

    source = await _mk_source(db)
    tag = str(ULID()).lower()[:6]
    model = AIModel(canonical_name=f"CurWalk-{tag}", slug=f"cw-{tag}")
    db.add(model)
    await db.flush()
    obs = EcosystemObservation(
        source_id=source.id, event_type="catalog_snapshot",
        canonical_entity_kind="model", canonical_entity_id=model.id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
    )
    db.add(obs)
    await db.flush()
    created = []
    for i in range(7):
        change = ChangeEvent(
            observation_id=obs.id, change_type="license", field=f"f{i}",
            old_value=None, new_value={"i": i},
            severity="info", entity_kind="model", canonical_entity_id=model.id,
        )
        db.add(change)
        await db.flush()
        created.append(change.id)

    from app.ecosystem.api.observations import list_changes

    seen: list[str] = []
    cursor = None
    for _ in range(10):
        out = await list_changes(
            change_type=None, severity=None, acknowledged=None,
            canonical_entity_id=model.id, cursor=cursor, limit=3, offset=0,
            db=db, _user=None,
        )
        seen.extend(r["id"] for r in out["data"])
        if not out["meta"]["has_more"]:
            break
        cursor = out["meta"]["next_cursor"]
    assert sorted(seen) == sorted(created), (len(seen), len(created))
    assert len(seen) == len(set(seen)), "duplicates across pages"

async def test_delta_export_does_not_skip_same_timestamp_rows(db):
    """Round-194 killer: three changes sharing one detected_at (a batch
    insert), page size 2 — following next_since/next_since_id must yield all
    three. A bare `detected_at > since` cursor silently drops ties."""
    from datetime import UTC, datetime

    from app.ecosystem.api.dashboard import export_changes_delta
    from app.ecosystem.models.catalog import AIModel

    source = await _mk_source(db)
    tag = str(ULID()).lower()[:6]
    model = AIModel(canonical_name=f"Delta-{tag}", slug=f"dl-{tag}")
    db.add(model)
    await db.flush()
    obs = EcosystemObservation(
        source_id=source.id, event_type="catalog_snapshot",
        canonical_entity_kind="model", canonical_entity_id=model.id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
    )
    db.add(obs)
    await db.flush()
    stamp = datetime(2026, 9, 25, 12, 0, 0, tzinfo=UTC)
    created = []
    for i in range(3):
        change = ChangeEvent(
            observation_id=obs.id, change_type="license", field=f"tie{i}",
            old_value=None, new_value={"i": i}, severity="info",
            entity_kind="model", canonical_entity_id=model.id,
            detected_at=stamp,
        )
        db.add(change)
        await db.flush()
        created.append(change.id)

    seen: list[str] = []
    since = "2026-09-25T11:59:59Z"
    since_id = None
    for _ in range(5):
        out = await export_changes_delta(
            since=since, since_id=since_id, limit=2, db=db, _user=None
        )
        seen.extend(r["id"] for r in out["data"] if r["id"] in created)
        if not out["meta"]["has_more"]:
            break
        since = out["meta"]["next_since"]
        since_id = out["meta"].get("next_since_id")
    assert sorted(seen) == sorted(created), f"lost ties: {len(seen)}/3"
