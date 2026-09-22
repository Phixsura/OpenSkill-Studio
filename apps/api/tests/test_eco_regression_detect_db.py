"""Round-13 tests (ADR-016 §22): automatic benchmark regression detection."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.benchmark import BenchmarkRun
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.observation import ChangeEvent
from app.ecosystem.services.benchmark import BenchmarkService
from tests.test_eco_services_db import _mk_suite_with_cases, _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def _run(suite_id, entity_id, *, mean, std, n, status="completed", hours_ago=1):
    return BenchmarkRun(
        suite_id=suite_id,
        status=status,
        target={"entity_kind": "model", "entity_id": entity_id},
        dimension_scores={
            "reliability": mean,
            "dimension_stats": {"reliability": {"mean": mean, "std": std, "n": n}},
        },
        finished_at=datetime.now(UTC) - timedelta(hours=hours_ago),
    )


async def test_significant_drop_emits_degraded_change(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin)
    model = AIModel(canonical_name="RegGen", slug=f"reggen-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    db.add(_run(suite.id, model.id, mean=0.95, std=0.02, n=20, hours_ago=24))
    new_run = _run(suite.id, model.id, mean=0.60, std=0.05, n=20, hours_ago=0)
    db.add(new_run)
    await db.flush()

    await BenchmarkService(db)._detect_regression(new_run)
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.field == "benchmark_regression",
            ChangeEvent.canonical_entity_id == model.id,
        )
    )
    assert change is not None
    assert change.severity == "degraded"
    assert change.change_type == "benchmark"
    regs = change.new_value["regressions"]
    assert regs[0]["dimension"] == "reliability"
    assert regs[0]["p_value"] < 0.05
    assert change.old_value["run_id"] != change.new_value["run_id"]


async def test_insignificant_or_improved_runs_stay_silent(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin)
    model = AIModel(canonical_name="StableGen", slug=f"stgen-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    db.add(_run(suite.id, model.id, mean=0.90, std=0.10, n=5, hours_ago=24))
    svc = BenchmarkService(db)
    # Tiny, statistically insignificant wobble (detected at ITS completion time)
    wobble = _run(suite.id, model.id, mean=0.89, std=0.10, n=5, hours_ago=1)
    db.add(wobble)
    await db.flush()
    await svc._detect_regression(wobble)
    # Clear improvement — never a regression
    better = _run(suite.id, model.id, mean=0.99, std=0.01, n=20, hours_ago=0)
    db.add(better)
    await db.flush()
    await svc._detect_regression(better)
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.field == "benchmark_regression",
            ChangeEvent.canonical_entity_id == model.id,
        )
    )
    assert change is None


async def test_first_run_for_target_has_no_baseline(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin)
    model = AIModel(canonical_name="FreshGen", slug=f"frgen-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    only = _run(suite.id, model.id, mean=0.5, std=0.1, n=10)
    db.add(only)
    await db.flush()
    await BenchmarkService(db)._detect_regression(only)  # must not raise
    change = await db.scalar(
        select(ChangeEvent).where(ChangeEvent.canonical_entity_id == model.id)
    )
    assert change is None
