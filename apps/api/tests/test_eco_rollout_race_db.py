"""Round-41 tests (ADR-016 §47): rollout decide race + stuck-run sweep."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.benchmark import BenchmarkRun
from app.ecosystem.models.replacement import ReplacementEdge
from app.ecosystem.services.replacement import ReplacementService
from app.ecosystem.services.rollout import RolloutService
from app.ecosystem.worker import sweep_stuck_runs
from app.exceptions import AppError
from tests.test_eco_services_db import _mk_model_version, _mk_suite_with_cases, _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def test_concurrent_promote_records_edge_once(db):
    admin = await _mk_user(db, "admin")
    deprecated = await _mk_model_version(db, "RaceOld")
    await _mk_model_version(db, "RaceNew")
    ranked, _ = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    svc = RolloutService(db)
    plan = await svc.create(
        replacement_candidate_id=ranked[0].id, scope_type="benchmark_only"
    )
    await svc.start(plan.id)
    await svc.evaluate(plan.id)
    await db.commit()
    plan_id, actor, dep_id = plan.id, admin.id, deprecated.id

    async def promote():
        async with AsyncSessionLocal() as session:
            try:
                await RolloutService(session).decide(
                    plan_id, decision="promote", actor_id=actor
                )
                await session.commit()
                return "promoted"
            except AppError as exc:
                await session.rollback()
                return exc.code

    results = await asyncio.gather(promote(), promote())
    assert sorted(results) == ["ECO_INVALID_TRANSITION", "promoted"], results
    async with AsyncSessionLocal() as session:
        edges = list(await session.scalars(
            select(ReplacementEdge).where(
                ReplacementEdge.from_id == dep_id,
                ReplacementEdge.edge_type == "recommended_replacement",
            )
        ))
        assert len(edges) == 1  # side effect recorded exactly once


async def test_stuck_running_runs_are_closed_not_zombied(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin)
    stuck = BenchmarkRun(
        suite_id=suite.id, status="running",
        target={"entity_kind": "model", "entity_id": "0" * 26},
        started_at=datetime.now(UTC) - timedelta(hours=6),
    )
    fresh = BenchmarkRun(
        suite_id=suite.id, status="running",
        target={"entity_kind": "model", "entity_id": "1" * 26},
        started_at=datetime.now(UTC) - timedelta(minutes=10),
    )
    db.add_all([stuck, fresh])
    await db.flush()

    n = await sweep_stuck_runs(db, max_running_hours=4)
    assert n == 1
    await db.refresh(stuck)
    await db.refresh(fresh)
    assert stuck.status == "failed" and "ECO_RUN_STUCK" in (stuck.error or "")
    assert stuck.finished_at is not None
    assert fresh.status == "running"  # recent runs untouched
    # Idempotent
    assert await sweep_stuck_runs(db, max_running_hours=4) == 0
