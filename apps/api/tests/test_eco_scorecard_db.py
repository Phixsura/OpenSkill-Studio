"""Round-14 tests (ADR-016 §23): Backstage-style entity scorecard."""

from datetime import UTC, datetime, timedelta

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.mapping import AvailabilityRecord
from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.services.catalog import CatalogService
from app.exceptions import AppError
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

async def test_trending_ranks_by_velocity_with_corroboration(db):
    from datetime import UTC, datetime, timedelta

    from app.ecosystem.services.dashboard import DashboardService

    hot = AIModel(canonical_name="HotGen", slug=f"hot-{str(ULID()).lower()}")
    cold = AIModel(canonical_name="ColdGen", slug=f"cold-{str(ULID()).lower()}")
    db.add_all([hot, cold])
    await db.flush()
    now = datetime.now(UTC)
    s1 = await _mk_source(db)
    s2 = await _mk_source(db)
    # hot: 4 obs this week from 2 sources, 1 last week → velocity 4.0
    for i, src in enumerate([s1, s1, s2, s2]):
        db.add(EcosystemObservation(
            source_id=src.id, event_type="model_released",
            canonical_entity_kind="model", canonical_entity_id=hot.id,
            raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
            observed_at=now - timedelta(days=1, hours=i),
        ))
    db.add(EcosystemObservation(
        source_id=s1.id, event_type="model_released",
        canonical_entity_kind="model", canonical_entity_id=hot.id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
        observed_at=now - timedelta(days=10),
    ))
    # cold: 1 obs this week
    db.add(EcosystemObservation(
        source_id=s1.id, event_type="model_released",
        canonical_entity_kind="model", canonical_entity_id=cold.id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
        observed_at=now - timedelta(days=2),
    ))
    await db.flush()

    # limit large enough that committed rows from other tests can't crowd
    # these fixtures out of the page (top-N truncation isn't under test)
    rows = await DashboardService(db).trending(days=7, limit=500)
    by_id = {r["entity_id"]: r for r in rows}
    assert by_id[hot.id]["observations"] == 4
    assert by_id[hot.id]["distinct_sources"] == 2
    assert by_id[hot.id]["velocity"] == 4.0
    assert by_id[hot.id]["canonical_name"] == "HotGen"
    assert by_id[cold.id]["velocity"] is None  # new, not infinite
    # hot ranks above cold
    ids = [r["entity_id"] for r in rows]
    assert ids.index(hot.id) < ids.index(cold.id)

    with pytest.raises(AppError):
        await DashboardService(db).trending(days=0)

async def test_single_source_corroboration_is_warn_not_pass(db):
    """Mutation-audit killer: ONE unverified source is a warn — corroboration
    means at least two distinct sources (or human verification), never one."""
    model = AIModel(
        canonical_name=f"OneSrcGen-{str(ULID()).lower()[:6]}",
        slug=f"os-{str(ULID()).lower()}", lifecycle_status="verified",
    )
    db.add(model)
    await db.flush()
    source = await _mk_source(db)
    db.add(EcosystemObservation(
        source_id=source.id, event_type="model_released",
        canonical_entity_kind="model", canonical_entity_id=model.id,
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
        observed_at=datetime.now(UTC) - timedelta(days=1),
    ))
    await db.flush()
    card = await CatalogService(db).scorecard("model", model.id)
    by_key = {c["check"]: c for c in card["checks"]}
    assert by_key["corroboration"]["status"] == "warn"
    assert by_key["corroboration"]["evidence"]["distinct_sources"] == 1
