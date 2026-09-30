"""Round-127 (ADR-016 §3.12): concurrent watch-item dedupe race."""

import asyncio

import pytest
from sqlalchemy import delete, select

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.replacement import WatchItem, Watchlist
from app.ecosystem.services.watchlists import WatchlistService
from tests.test_eco_services_db import _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def test_concurrent_add_item_inserts_exactly_once(db):
    """Two sessions racing add_item for the same target must yield ONE row —
    the service-level probe alone lost this race before the R127 partial
    unique indexes; a duplicate row doubles every notification."""
    user = await _mk_user(db)
    wl = await WatchlistService(db).create(owner_id=user.id, name="RaceWatch")
    await db.commit()
    wl_id, owner_id = wl.id, user.id

    async def add():
        async with AsyncSessionLocal() as session:
            item = await WatchlistService(session).add_item(
                wl_id, owner_id, target_kind="github_repo", target_ref="race/repo"
            )
            await session.commit()
            return item.id

    try:
        ids = await asyncio.gather(add(), add())
        assert ids[0] == ids[1], f"race inserted two rows: {ids}"
        async with AsyncSessionLocal() as session:
            rows = list(
                await session.scalars(
                    select(WatchItem).where(WatchItem.watchlist_id == wl_id)
                )
            )
            assert len(rows) == 1
    finally:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(WatchItem).where(WatchItem.watchlist_id == wl_id))
            await session.execute(delete(Watchlist).where(Watchlist.id == wl_id))
            await session.commit()
