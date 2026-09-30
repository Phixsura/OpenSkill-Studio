"""Round-34 tests (ADR-016 §40): query budgets — N+1 stays dead.

Counts real SQL statements via a cursor-execute event listener; a budget
breach means someone reintroduced a per-row query loop.
"""

from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import event
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.services.dashboard import DashboardService
from tests.test_eco_services_db import _mk_source


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@contextmanager
def count_statements():
    from app.core.database import engine

    counter = {"n": 0}

    def _before(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            counter["n"] += 1

    sync_engine = engine.sync_engine
    event.listen(sync_engine, "before_cursor_execute", _before)
    try:
        yield counter
    finally:
        event.remove(sync_engine, "before_cursor_execute", _before)


async def test_trending_has_constant_query_count(db):
    source = await _mk_source(db)
    now = datetime.now(UTC)
    # 12 distinct trending entities — a per-row prev-window query would blow the budget
    for i in range(12):
        model = AIModel(canonical_name=f"QB-{i}-{str(ULID()).lower()[:6]}", slug=f"qb{i}-{str(ULID()).lower()}")
        db.add(model)
        await db.flush()
        db.add(EcosystemObservation(
            source_id=source.id, event_type="model_released",
            canonical_entity_kind="model", canonical_entity_id=model.id,
            raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
            observed_at=now - timedelta(days=1),
        ))
    await db.flush()

    svc = DashboardService(db)
    with count_statements() as counter:
        rows = await svc.trending(days=7, limit=12)
    assert len(rows) >= 12
    # 1 grouped current-window + 1 grouped prev-window + ≤1 entity-name lookup
    # per row (get() may hit identity map) — generous ceiling that still
    # catches an O(rows) prev-window loop (which would add 12+ SELECTs alone)
    assert counter["n"] <= 3 + 12, f"query budget blown: {counter['n']}"


async def test_overview_and_coverage_stay_within_budget(db):
    svc = DashboardService(db)
    with count_statements() as counter:
        await svc.overview()
    assert counter["n"] <= 25, f"overview budget blown: {counter['n']}"
    with count_statements() as counter:
        await svc.coverage()
    assert counter["n"] <= 15, f"coverage budget blown: {counter['n']}"
