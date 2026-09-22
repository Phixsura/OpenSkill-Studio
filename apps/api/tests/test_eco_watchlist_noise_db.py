"""Round-16 tests (ADR-016 §24): watchlist noise controls."""

from datetime import UTC, datetime, timedelta

import pytest
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
