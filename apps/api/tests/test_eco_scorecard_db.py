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

async def test_dashboard_coverage_counts_evidence_dimensions(db):
    from app.ecosystem.models.mapping import CapabilityMapping, PriceObservation
    from app.ecosystem.services.dashboard import DashboardService
    from tests.test_eco_services_db import _mk_capability_tag, _mk_source

    covered = AIModel(canonical_name="CoveredGen", slug=f"cov-{str(ULID()).lower()}")
    bare = AIModel(canonical_name="BareGen2", slug=f"bare2-{str(ULID()).lower()}")
    db.add_all([covered, bare])
    await db.flush()
    await _mk_capability_tag(db, "image_generation")
    db.add(CapabilityMapping(
        entity_kind="model", entity_id=covered.id, capability_key="image_generation",
        evidence_level="vendor_claimed",
        io_spec={"inputs": [{"type": "text"}], "outputs": [{"type": "image"}]},
    ))
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="pricing_changed",
        canonical_entity_kind="model", canonical_entity_id=covered.id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
    )
    db.add(obs)
    await db.flush()
    db.add(PriceObservation(
        observation_id=obs.id, entity_kind="model", entity_id=covered.id,
        unit="image", price=0.04, currency="USD",
    ))
    await db.flush()

    cov = await DashboardService(db).coverage()
    models = cov["model"]
    assert models["total"] >= 2
    assert models["with_capability_mapping"] >= 1
    assert models["with_pricing"] >= 1
    # every catalog kind is present with all four counters
    for kind_stats in cov.values():
        assert set(kind_stats) == {
            "total", "with_capability_mapping", "with_benchmark", "with_pricing"
        }
