"""Round-14 tests (ADR-016 §23): Backstage-style entity scorecard."""

from datetime import UTC, datetime, timedelta

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.mapping import AvailabilityRecord
from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.services.catalog import CatalogService
from tests.test_eco_services_db import _mk_source


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def test_scorecard_bare_entity_is_honest_about_unknowns(db):
    model = AIModel(
        canonical_name="BareGen", slug=f"bare-{str(ULID()).lower()}",
        lifecycle_status="discovered",
    )
    db.add(model)
    await db.flush()

    card = await CatalogService(db).scorecard("model", model.id)
    by_key = {c["check"]: c for c in card["checks"]}
    # Never probed/benchmarked/priced → n/a, NOT failures
    assert by_key["availability"]["status"] == "n/a"
    assert by_key["benchmark"]["status"] == "n/a"
    assert by_key["pricing"]["status"] == "n/a"
    # Never observed → freshness fails; single-source corroboration fails too
    assert by_key["freshness"]["status"] == "fail"
    assert by_key["corroboration"]["status"] == "fail"
    assert by_key["lifecycle"]["status"] == "warn"
    assert card["grade"] == "failing"
    assert card["applicable"] == 3  # n/a checks excluded from the denominator


async def test_scorecard_corroborated_fresh_operational_entity(db):
    model = AIModel(
        canonical_name="HealthyGen", slug=f"heal-{str(ULID()).lower()}",
        lifecycle_status="verified",
    )
    db.add(model)
    await db.flush()
    for i in range(2):  # two DISTINCT sources
        source = await _mk_source(db)
        db.add(EcosystemObservation(
            source_id=source.id, event_type="model_released",
            canonical_entity_kind="model", canonical_entity_id=model.id,
            raw_hash=f"{i}s" * 32, normalized={},
            observed_at=datetime.now(UTC) - timedelta(days=1),
        ))
    db.add(AvailabilityRecord(
        entity_kind="model", entity_id=model.id, record_type="status",
        value={"status": "operational"},
        observed_at=datetime.now(UTC) - timedelta(hours=2),
    ))
    await db.flush()

    card = await CatalogService(db).scorecard("model", model.id)
    by_key = {c["check"]: c for c in card["checks"]}
    assert by_key["lifecycle"]["status"] == "pass"
    assert by_key["corroboration"]["status"] == "pass"
    assert by_key["freshness"]["status"] == "pass"
    assert by_key["availability"]["status"] == "pass"
    assert card["grade"] == "healthy"
    # Every check carries evidence, never a bare verdict
    assert all(c["evidence"] for c in card["checks"])
