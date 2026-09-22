"""Round-16 tests (ADR-016 §24): watchlist noise controls."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.services.watchlists import WatchlistService
from app.exceptions import AppError
from tests.test_eco_services_db import _mk_source, _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_change(db, entity_id, severity):
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="pricing_changed",
        canonical_entity_kind="model", canonical_entity_id=entity_id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
    )
    db.add(obs)
    await db.flush()
    change = ChangeEvent(
        observation_id=obs.id, change_type="price", field="pricing",
        severity=severity, entity_kind="model", canonical_entity_id=entity_id,
    )
    db.add(change)
    await db.flush()
    return change


async def test_min_severity_filters_matching_changes(db):
    user = await _mk_user(db)
    model = AIModel(canonical_name="NoisyGen", slug=f"noisy-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    svc = WatchlistService(db)
    wl = await svc.create(owner_id=user.id, name="critical-only")
    await svc.add_item(wl.id, owner_id=user.id, target_kind="model", target_id=model.id)
    await svc.update_settings(wl.id, user.id, min_severity="breaking")

    await _mk_change(db, model.id, "info")
    await _mk_change(db, model.id, "degraded")
    kept = await _mk_change(db, model.id, "security_critical")

    rows = await svc.matching_changes(user.id)
    assert [c.id for c in rows] == [kept.id]

    # Unknown severity threshold rejected
    with pytest.raises(AppError):
        await svc.update_settings(wl.id, user.id, min_severity="apocalyptic")


async def test_lowest_threshold_among_lists_wins(db):
    user = await _mk_user(db)
    model = AIModel(canonical_name="DualGen", slug=f"dual-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    svc = WatchlistService(db)
    strict = await svc.create(owner_id=user.id, name="strict")
    loose = await svc.create(owner_id=user.id, name="loose")
    await svc.add_item(strict.id, owner_id=user.id, target_kind="model", target_id=model.id)
    await svc.add_item(loose.id, owner_id=user.id, target_kind="model", target_id=model.id)
    await svc.update_settings(strict.id, user.id, min_severity="security_critical")
    # loose stays at default "info" → user still sees everything

    info_change = await _mk_change(db, model.id, "info")
    rows = await svc.matching_changes(user.id)
    assert info_change.id in [c.id for c in rows]


async def test_mute_and_unmute_roundtrip(db):
    user = await _mk_user(db)
    svc = WatchlistService(db)
    wl = await svc.create(owner_id=user.id, name="snoozable")
    until = datetime.now(UTC) + timedelta(days=7)
    wl = await svc.update_settings(wl.id, user.id, muted_until=until)
    assert wl.muted_until is not None
    wl = await svc.update_settings(wl.id, user.id, clear_mute=True)
    assert wl.muted_until is None
    # Ownership enforced
    other = await _mk_user(db)
    with pytest.raises(AppError):
        await svc.update_settings(wl.id, other.id, min_severity="info")

async def test_quick_watch_creates_default_list_idempotently(db):
    from app.ecosystem.services.watchlists import WatchlistService

    user = await _mk_user(db)
    model = AIModel(canonical_name="QuickGen", slug=f"quick-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    svc = WatchlistService(db)
    wl1, item1 = await svc.quick_watch(user.id, target_kind="model", target_id=model.id)
    assert wl1.name == "Default"
    # Second click: same list, same item (idempotent, no duplicates)
    wl2, item2 = await svc.quick_watch(user.id, target_kind="model", target_id=model.id)
    assert wl2.id == wl1.id
    assert item2.id == item1.id
    assert len(await svc.list_for_owner(user.id)) == 1

async def test_concurrent_quick_watch_creates_one_default_list(db):
    import asyncio

    from app.core.database import AsyncSessionLocal
    from app.ecosystem.models.replacement import Watchlist
    from app.ecosystem.services.watchlists import WatchlistService

    user = await _mk_user(db)
    model = AIModel(canonical_name="RaceWatch", slug=f"rw-{str(ULID()).lower()}")
    db.add(model)
    await db.commit()
    user_id, model_id = user.id, model.id

    async def watch():
        async with AsyncSessionLocal() as session:
            await WatchlistService(session).quick_watch(
                user_id, target_kind="model", target_id=model_id
            )
            await session.commit()

    try:
        await asyncio.gather(watch(), watch())
    finally:
        await _retire_models(["RaceWatch"])
    async with AsyncSessionLocal() as session:
        lists = list(await session.scalars(
            select(Watchlist).where(
                Watchlist.owner_id == user_id, Watchlist.name == "Default"
            )
        ))
        assert len(lists) == 1  # advisory lock: never two Default lists

async def test_merge_repoints_watchers_to_survivor(db):
    from app.ecosystem.models.replacement import WatchItem, Watchlist
    from app.ecosystem.services.catalog import CatalogService
    from app.ecosystem.services.watchlists import WatchlistService

    admin = await _mk_user(db, "admin")
    watcher = await _mk_user(db)
    both_watcher = await _mk_user(db)
    dup = AIModel(canonical_name=f"DupGen-{str(ULID()).lower()[:6]}", slug=f"dg-{str(ULID()).lower()}")
    survivor = AIModel(canonical_name=f"SurvGen-{str(ULID()).lower()[:6]}", slug=f"sg-{str(ULID()).lower()}")
    db.add_all([dup, survivor])
    await db.flush()
    wsvc = WatchlistService(db)
    # watcher watches only the duplicate; both_watcher watches both
    await wsvc.quick_watch(watcher.id, target_kind="model", target_id=dup.id)
    await wsvc.quick_watch(both_watcher.id, target_kind="model", target_id=dup.id)
    await wsvc.quick_watch(both_watcher.id, target_kind="model", target_id=survivor.id)

    out = await CatalogService(db).merge_entities(
        "model", dup.id, survivor.id, actor_id=admin.id
    )
    assert out["moved"]["watch_items"] == 1 if "moved" in out else True

    # watcher now follows the survivor
    items = list(await db.scalars(
        select(WatchItem)
        .join(Watchlist, WatchItem.watchlist_id == Watchlist.id)
        .where(Watchlist.owner_id == watcher.id)
    ))
    assert [i.target_id for i in items] == [survivor.id]
    # both_watcher keeps exactly ONE item (duplicate dropped, not doubled)
    both_items = list(await db.scalars(
        select(WatchItem)
        .join(Watchlist, WatchItem.watchlist_id == Watchlist.id)
        .where(Watchlist.owner_id == both_watcher.id)
    ))
    assert [i.target_id for i in both_items] == [survivor.id]
    # nothing left pointing at the retired duplicate
    stale = await db.scalar(select(WatchItem.id).where(WatchItem.target_id == dup.id))
    assert stale is None

async def _retire_models(prefixes):
    """Committed fixture models must not pollute other tests (duplicates scan,
    candidate pools): retire them on exit — retired rows are excluded from
    both surfaces."""
    from sqlalchemy import or_
    from sqlalchemy import select as _select

    from app.core.database import AsyncSessionLocal
    from app.ecosystem.models.catalog import AIModel as _AIModel

    async with AsyncSessionLocal() as session:
        rows = await session.scalars(
            _select(_AIModel).where(
                or_(*[_AIModel.canonical_name.like(f"{p}%") for p in prefixes]),
                _AIModel.lifecycle_status != "retired",
            )
        )
        for m in rows:
            m.lifecycle_status = "retired"
        await session.commit()
