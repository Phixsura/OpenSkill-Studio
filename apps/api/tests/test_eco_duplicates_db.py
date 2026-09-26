"""Round-21 tests (ADR-016 §29): entity-level duplicate detection sweep."""

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.services.catalog import CatalogService
from app.exceptions import AppError


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_model(db, name, lifecycle="verified"):
    model = AIModel(
        canonical_name=name, slug=f"m-{str(ULID()).lower()}",
        lifecycle_status=lifecycle,
    )
    db.add(model)
    await db.flush()
    return model


async def test_find_duplicates_surfaces_similar_pairs_once(db):
    tag = str(ULID()).lower()[:8]
    a = await _mk_model(db, f"FluxImage Pro {tag}")
    b = await _mk_model(db, f"Flux Image Pro {tag}")
    await _mk_model(db, f"TotallyDifferent {str(ULID()).lower()[:8]}")
    retired = await _mk_model(db, f"FluxImage Pro {tag} v2", lifecycle="retired")

    pairs = await CatalogService(db).find_duplicates("model", threshold=0.5, limit=200)
    ours = [
        p for p in pairs
        if {p["a"]["id"], p["b"]["id"]} == {a.id, b.id}
    ]
    assert len(ours) == 1  # reported once, not twice
    assert ours[0]["similarity"] >= 0.5
    # Retired entities never appear
    assert all(
        retired.id not in (p["a"]["id"], p["b"]["id"]) for p in pairs
    )


async def test_find_duplicates_validates_inputs(db):
    with pytest.raises(AppError):
        await CatalogService(db).find_duplicates("nonsense_kind")
    with pytest.raises(AppError):
        await CatalogService(db).find_duplicates("model", threshold=0.1)
