"""Round-40 tests (ADR-016 §46): merge + reconcile concurrency fences."""

import asyncio

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.mapping import PriceObservation
from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.services.catalog import CatalogService
from app.ecosystem.services.pricing import PricingService
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


async def test_opposite_direction_merges_have_one_winner(db):
    admin = await _mk_user(db, "admin")
    a = AIModel(canonical_name=f"MergeA-{str(ULID()).lower()[:6]}", slug=f"ma-{str(ULID()).lower()}")
    b = AIModel(canonical_name=f"MergeB-{str(ULID()).lower()[:6]}", slug=f"mb-{str(ULID()).lower()}")
    db.add_all([a, b])
    await db.commit()
    a_id, b_id, actor = a.id, b.id, admin.id

    async def merge(src, dst):
        async with AsyncSessionLocal() as session:
            try:
                await CatalogService(session).merge_entities("model", src, dst, actor_id=actor)
                await session.commit()
                return "merged"
            except AppError as exc:
                await session.rollback()
                return exc.code

    try:
        results = await asyncio.gather(merge(a_id, b_id), merge(b_id, a_id))
        assert sorted(results) == ["ECO_INVALID_TRANSITION", "merged"], results
    finally:
        pass  # verification below; cleanup at end of test

    async with AsyncSessionLocal() as session:
        ra = await session.get(AIModel, a_id)
        rb = await session.get(AIModel, b_id)
        # Exactly ONE side retired — never both
        assert sorted([ra.lifecycle_status == "retired", rb.lifecycle_status == "retired"]) == [
            False,
            True,
        ]
    await _retire_models(["MergeA-", "MergeB-"])


async def test_concurrent_price_approval_mints_once(db):
    admin = await _mk_user(db, "admin")
    model = AIModel(canonical_name=f"PriceRace-{str(ULID()).lower()[:6]}", slug=f"pr-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="pricing_changed",
        canonical_entity_kind="model", canonical_entity_id=model.id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
    )
    db.add(obs)
    await db.flush()
    row = PriceObservation(
        observation_id=obs.id, entity_kind="model", entity_id=model.id,
        unit="image", price=0.05, currency="USD",
    )
    db.add(row)
    await db.commit()
    row_id, actor = row.id, admin.id

    async def approve():
        async with AsyncSessionLocal() as session:
            try:
                await PricingService(session).reconcile(
                    row_id, decision="approve", actor_id=actor,
                    provider_key="test-provider", model_or_service="m",
                )
                await session.commit()
                return "approved"
            except AppError as exc:
                await session.rollback()
                return exc.code

    try:
        results = await asyncio.gather(approve(), approve())
        assert sorted(results) == ["ECO_INVALID_TRANSITION", "approved"], results
    finally:
        await _retire_models(["PriceRace-"])

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
