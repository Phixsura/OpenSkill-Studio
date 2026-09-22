"""Round-20 tests (ADR-016 §28): benchmark↔production divergence wiring."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.benchmark import BenchmarkRun
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.services.benchmark import BenchmarkService
from app.ecosystem.services.telemetry import TelemetryService
from tests.test_eco_services_db import _mk_source, _mk_suite_with_cases, _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _seed_entity_with_telemetry(db, *, success_rate):
    """Observation anchor + global telemetry snapshot for one entity id."""
    entity_id = str(ULID())
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="model_released",
        canonical_entity_kind="provider_offering", canonical_entity_id=entity_id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
    )
    db.add(obs)
    await db.flush()
    now = datetime.now(UTC)
    rows = [
        {"org_id": None, "succeeded": i < int(success_rate * 100), "retries": 0,
         "latency_ms": 100.0, "cost_usd": None, "error_code": None}
        for i in range(100)
    ]
    await TelemetryService(db).write_snapshot(
        entity_kind="provider_offering", entity_id=entity_id,
        window_start=now - timedelta(hours=1), window_end=now,
        rows=rows, org_id=None, contributing_orgs=5,
    )
    return entity_id


async def test_run_completion_flags_divergence_once(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin)
    entity_id = await _seed_entity_with_telemetry(db, success_rate=0.50)
    run = BenchmarkRun(
        suite_id=suite.id, status="completed",
        target={"entity_kind": "provider_offering", "entity_id": entity_id},
        dimension_scores={"reliability": 0.95},
        finished_at=datetime.now(UTC),
    )
    db.add(run)
    await db.flush()

    await BenchmarkService(db)._check_production_divergence(run)
    flags = list(await db.scalars(
        select(ChangeEvent).where(
            ChangeEvent.canonical_entity_id == entity_id,
            ChangeEvent.field == "benchmark_production_divergence",
        )
    ))
    assert len(flags) == 1
    assert flags[0].severity == "degraded"
    assert flags[0].old_value["benchmark_reliability"] == 0.95

    # Idempotent while the flag is unacknowledged
    await BenchmarkService(db)._check_production_divergence(run)
    flags = list(await db.scalars(
        select(ChangeEvent).where(
            ChangeEvent.canonical_entity_id == entity_id,
            ChangeEvent.field == "benchmark_production_divergence",
        )
    ))
    assert len(flags) == 1


async def test_agreeing_numbers_never_flag(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin)
    entity_id = await _seed_entity_with_telemetry(db, success_rate=0.93)
    run = BenchmarkRun(
        suite_id=suite.id, status="completed",
        target={"entity_kind": "provider_offering", "entity_id": entity_id},
        dimension_scores={"reliability": 0.95},
        finished_at=datetime.now(UTC),
    )
    db.add(run)
    await db.flush()
    await BenchmarkService(db)._check_production_divergence(run)
    flag = await db.scalar(
        select(ChangeEvent.id).where(
            ChangeEvent.canonical_entity_id == entity_id,
            ChangeEvent.field == "benchmark_production_divergence",
        )
    )
    assert flag is None
