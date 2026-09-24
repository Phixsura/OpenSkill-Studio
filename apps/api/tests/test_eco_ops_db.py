"""Round-6 distributed-correctness & ops-hygiene tests (ADR-016 §16).

Benchmark run claim fencing, source-sync row-level mutual exclusion,
availability/sync-run retention pruning (flips preserved), stale-source
monitoring, distributed rate-limiter wiring.
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.mapping import AvailabilityRecord
from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.models.source import SourceSyncRun
from app.ecosystem.services.benchmark import BenchmarkService
from app.ecosystem.services.dashboard import DashboardService
from app.ecosystem.services.pricing import AvailabilityService
from app.ecosystem.services.sync import SyncService
from app.ecosystem.worker import prune_ecosystem_history
from app.exceptions import AppError
from tests.test_eco_services_db import (
    _catalog_payload,
    _fetcher_for,
    _mk_model_version,
    _mk_source,
    _mk_suite_with_cases,
    _mk_user,
)


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


# ── Benchmark run claim fencing ─────────────────────────────────────


async def test_run_claim_fencing_blocks_second_worker(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin, n_cases=1)
    bench = BenchmarkService(db)
    run = await bench.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "F" * 26}
    )
    # Simulate a concurrent worker having claimed the run between the status
    # read and the claim UPDATE: flip the row out from under this executor.
    from sqlalchemy import update

    from app.ecosystem.models.benchmark import BenchmarkRun

    original_execute = db.execute
    fenced = {"done": False}

    async def racing_execute(stmt, *args, **kwargs):
        # First claim attempt loses the race: another worker already flipped it
        if (
            not fenced["done"]
            and getattr(stmt, "is_update", False)
            and stmt.table.name == "eco_benchmark_runs"
        ):
            fenced["done"] = True
            await original_execute(
                update(BenchmarkRun)
                .where(BenchmarkRun.id == run.id)
                .values(status="running")
            )
        return await original_execute(stmt, *args, **kwargs)

    db.execute = racing_execute
    try:
        with pytest.raises(AppError) as exc:
            await bench.execute_run(run.id)
    finally:
        db.execute = original_execute
    assert exc.value.code == "ECO_INVALID_TRANSITION"
    assert "claimed by another worker" in exc.value.message
    # No results were produced by the losing worker
    assert await bench.list_results(run.id) == []


async def test_run_executes_normally_without_race(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin, n_cases=1)
    bench = BenchmarkService(db)
    run = await bench.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "G" * 26}
    )
    run = await bench.execute_run(run.id)
    assert run.status == "completed"


# ── Source sync mutual exclusion ────────────────────────────────────


async def test_concurrent_sync_second_session_skips(db):
    source = await _mk_source(db)
    source_id = source.id
    # A second SESSION must see the source → commit it (cleaned up below)
    await db.commit()
    body = _catalog_payload([{"id": f"mx-{ULID()}", "name": "MX", "version": "1"}])
    from sqlalchemy import select as sa_select

    from app.ecosystem.models.source import EcosystemSource

    try:
        # Session A takes the row lock (a sync in flight)
        await db.execute(
            sa_select(EcosystemSource.id)
            .where(EcosystemSource.id == source_id)
            .with_for_update()
        )
        # Session B (a second worker) must skip immediately — not block,
        # not duplicate the fetch
        async with AsyncSessionLocal() as other:
            with pytest.raises(AppError) as exc:
                await SyncService(other, fetcher=_fetcher_for(body)).run_sync(source_id)
            assert exc.value.code == "ECO_SYNC_IN_PROGRESS"
            await other.rollback()
        # Same-session (same transaction) re-entry works — lock is reentrant
        run = await SyncService(db, fetcher=_fetcher_for(body)).run_sync(source_id)
        assert run.status == "success"
        await db.rollback()  # discard the sync's rows before cleanup
    finally:
        from sqlalchemy import delete

        from app.ecosystem.models.observation import ChangeEvent
        from app.ecosystem.models.source import SourceSyncRun

        obs_ids = sa_select(EcosystemObservation.id).where(
            EcosystemObservation.source_id == source_id
        )
        await db.execute(delete(ChangeEvent).where(ChangeEvent.observation_id.in_(obs_ids)))
        await db.execute(
            delete(EcosystemObservation).where(EcosystemObservation.source_id == source_id)
        )
        await db.execute(delete(SourceSyncRun).where(SourceSyncRun.source_id == source_id))
        await db.execute(delete(EcosystemSource).where(EcosystemSource.id == source_id))
        await db.commit()


# ── Retention pruning ───────────────────────────────────────────────


async def test_retention_prunes_old_probes_keeps_latest_and_flip_evidence(db):
    version = await _mk_model_version(db, f"Ret{str(ULID())[-4:]}")
    svc = AvailabilityService(db)
    old = datetime.now(UTC) - timedelta(days=120)
    # Three old redundant probes + one fresh
    for i in range(3):
        record = await svc.record(
            entity_kind="model_version", entity_id=version.id,
            record_type="status", value={"status": "operational"},
        )
        record.observed_at = old + timedelta(hours=i)
    fresh = await svc.record(
        entity_kind="model_version", entity_id=version.id,
        record_type="status", value={"status": "operational"},
    )
    # An old NON-status record must never be touched
    rate = await svc.record(
        entity_kind="model_version", entity_id=version.id,
        record_type="rate_limit", value={"requests_per_minute": 60},
    )
    rate.observed_at = old
    await db.flush()
    pruned = await prune_ecosystem_history(db)
    assert pruned["availability_status_pruned"] == 3
    remaining = list(
        await db.scalars(
            select(AvailabilityRecord).where(AvailabilityRecord.entity_id == version.id)
        )
    )
    kinds = sorted(r.record_type for r in remaining)
    assert kinds == ["rate_limit", "status"]
    assert any(r.id == fresh.id for r in remaining)


async def test_retention_prunes_old_sync_runs_only(db):
    source = await _mk_source(db)
    body = _catalog_payload([{"id": f"rr-{ULID()}", "name": "RR", "version": "1"}])
    run = await SyncService(db, fetcher=_fetcher_for(body)).run_sync(source.id)
    ancient = SourceSyncRun(
        source_id=source.id, status="success", parser_version="1.0",
    )
    db.add(ancient)
    await db.flush()
    ancient.started_at = datetime.now(UTC) - timedelta(days=200)
    await db.flush()
    pruned = await prune_ecosystem_history(db)
    assert pruned["sync_runs_pruned"] == 1
    # Recent run + its append-only observation survive
    assert await db.get(SourceSyncRun, run.id) is not None
    obs = await db.scalar(
        select(EcosystemObservation).where(EcosystemObservation.source_id == source.id)
    )
    assert obs is not None


# ── Stale source monitoring ─────────────────────────────────────────


async def test_dashboard_counts_stale_sources(db):
    healthy = await _mk_source(db, name=f"h-{ULID()}", sync_interval_minutes=60)
    healthy.last_success_at = datetime.now(UTC) - timedelta(minutes=30)
    stale = await _mk_source(db, name=f"st-{ULID()}", sync_interval_minutes=60)
    stale.last_success_at = datetime.now(UTC) - timedelta(hours=5)  # > 3× interval
    paused = await _mk_source(db, name=f"p-{ULID()}", sync_interval_minutes=60)
    paused.status = "paused"
    paused.last_success_at = datetime.now(UTC) - timedelta(days=9)
    await db.flush()
    overview = await DashboardService(db).overview()
    assert overview["sources_stale"] >= 1  # stale counted; paused excluded


# ── Distributed rate limiter wiring ─────────────────────────────────


def test_eco_router_uses_redis_backed_limiter():
    import inspect

    import app.ecosystem.api as eco_api

    src = inspect.getsource(eco_api)
    assert "from app.core.rate_limit import rate_limit" in src
    assert "rate_limit(120, 60)" in src
    assert "rate_limit_talent" not in src  # in-memory limiter fully replaced

async def test_prune_keeps_each_entitys_latest_status_row(db):
    """Mutation-audit killer: an entity last probed BEFORE the cutoff keeps
    exactly its latest status row — pruning it would flip current_status to
    unknown and erase the survivor's only availability evidence."""
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select as _select

    from app.ecosystem.models.mapping import AvailabilityRecord
    from app.ecosystem.worker import prune_ecosystem_history

    entity_id = str(ULID())
    old = datetime.now(UTC) - timedelta(days=200)
    for i in range(3):
        db.add(AvailabilityRecord(
            entity_kind="model", entity_id=entity_id, record_type="status",
            value={"status": "operational"},
            observed_at=old + timedelta(days=i),
        ))
    await db.flush()
    await prune_ecosystem_history(db)
    rows = list(await db.scalars(
        _select(AvailabilityRecord).where(AvailabilityRecord.entity_id == entity_id)
    ))
    assert len(rows) == 1  # only redundant older samples pruned
    assert rows[0].observed_at.replace(tzinfo=UTC) == (old + timedelta(days=2))


async def test_prune_keeps_recent_raw_snapshots(db):
    """Mutation-audit killer: raw snapshots inside the 90-day window survive
    pruning — a zeroed window would destroy the replay capability."""
    import hashlib
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select as _select

    from app.ecosystem.models.source import RawSnapshot
    from app.ecosystem.worker import prune_ecosystem_history
    from tests.test_eco_services_db import _mk_source

    source = await _mk_source(db)
    fresh = RawSnapshot(
        source_id=source.id, raw_hash=hashlib.sha256(str(ULID()).encode()).hexdigest(),
        content=b"{}", content_length=2, parser_version="1.0",
        fetched_at=datetime.now(UTC) - timedelta(days=5),
    )
    stale = RawSnapshot(
        source_id=source.id, raw_hash=hashlib.sha256(str(ULID()).encode()).hexdigest(),
        content=b"{}", content_length=2, parser_version="1.0",
        fetched_at=datetime.now(UTC) - timedelta(days=120),
    )
    db.add_all([fresh, stale])
    await db.flush()
    out = await prune_ecosystem_history(db)
    assert out["raw_snapshots_pruned"] >= 1
    remaining = {
        r.id for r in await db.scalars(
            _select(RawSnapshot).where(RawSnapshot.source_id == source.id)
        )
    }
    assert fresh.id in remaining     # inside the window: kept
    assert stale.id not in remaining  # outside: pruned

async def test_sync_scheduler_due_semantics(db):
    """Mutation-audit killers ×4: the continuous-discovery scheduler enqueues
    exactly the DUE ACTIVE sources — never-synced counts as due now; recently
    synced waits its interval; overdue re-enqueues; paused never enqueues."""
    from app.controlplane.models.outbox import OutboxMessage
    from app.ecosystem.worker import sweep_due_sources
    from tests.test_eco_services_db import _mk_source

    now = datetime.now(UTC)
    never = await _mk_source(db)                      # active, never synced → due
    fresh = await _mk_source(db)                      # active, just synced → not due
    fresh.last_sync_at = now - timedelta(minutes=1)
    fresh.sync_interval_minutes = 60
    overdue = await _mk_source(db)                    # active, way past interval → due
    overdue.last_sync_at = now - timedelta(hours=5)
    overdue.sync_interval_minutes = 60
    paused = await _mk_source(db)                     # paused → NEVER enqueued
    paused.status = "paused"
    paused.last_sync_at = now - timedelta(hours=99)
    await db.flush()

    n = await sweep_due_sources(db)
    msgs = list(await db.scalars(
        select(OutboxMessage).where(OutboxMessage.topic == "eco.sync_source")
    ))
    enqueued = {m.payload.get("source_id") for m in msgs}
    assert never.id in enqueued
    assert overdue.id in enqueued
    assert fresh.id not in enqueued
    assert paused.id not in enqueued
    assert n >= 2

async def test_hotpath_indexes_exist_in_db(db):
    """Round-137 killer: the two per-change-event hot-path indexes exist in
    the actual schema (migration eco08 applied and names match the models)."""
    from sqlalchemy import text

    rows = await db.execute(text(
        "SELECT indexname FROM pg_indexes WHERE indexname IN "
        "('ix_eco_watch_items_target', 'ix_eco_changes_canonical')"
    ))
    names = sorted(r[0] for r in rows)
    assert names == ["ix_eco_changes_canonical", "ix_eco_watch_items_target"], names

async def test_retention_prunes_stale_unreviewed_prices(db):
    """Round-153 killer: unreviewed price observations older than 180 days are
    pruned; DECIDED rows of the same age are kept (billing audit evidence)."""
    from datetime import UTC, datetime, timedelta

    from app.ecosystem.models.mapping import PriceObservation
    from app.ecosystem.worker import prune_ecosystem_history

    version = await _mk_model_version(db, "PrRet")
    source = await _mk_source(db)
    rows = {}
    for status in ("unreviewed", "approved"):
        obs = EcosystemObservation(
            source_id=source.id, event_type="pricing_changed",
            raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
        )
        db.add(obs)
        await db.flush()
        row = PriceObservation(
            observation_id=obs.id, entity_kind="model_version", entity_id=version.id,
            unit="token_input", price="0.01", currency="USD",
            reconciliation_status=status,
            observed_at=datetime.now(UTC) - timedelta(days=200),
        )
        db.add(row)
        await db.flush()
        rows[status] = row.id

    out = await prune_ecosystem_history(db)
    assert out["unreviewed_prices_pruned"] >= 1
    assert await db.get(PriceObservation, rows["unreviewed"]) is None
    assert await db.get(PriceObservation, rows["approved"]) is not None
