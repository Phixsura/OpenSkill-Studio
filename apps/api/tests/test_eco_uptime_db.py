"""Round-11 tests (ADR-016 §20): time-weighted uptime/SLO summary."""

from datetime import UTC, datetime, timedelta

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.mapping import AvailabilityRecord
from app.ecosystem.services.pricing import AvailabilityService
from app.exceptions import AppError


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_model(db, name):
    model = AIModel(canonical_name=name, slug=f"{name.lower()}-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    return model


def _status(entity_id, status, hours_ago):
    return AvailabilityRecord(
        entity_kind="model",
        entity_id=entity_id,
        record_type="status",
        value={"status": status},
        observed_at=datetime.now(UTC) - timedelta(hours=hours_ago),
    )


async def test_uptime_time_weighted_with_incident_count(db):
    model = await _mk_model(db, "UptimeGen")
    # 10h operational → 2h degraded → operational since (till now)
    db.add(_status(model.id, "operational", 12))
    db.add(_status(model.id, "degraded", 2))
    db.add(_status(model.id, "operational", 1))
    await db.flush()

    out = await AvailabilityService(db).uptime(
        entity_kind="model", entity_id=model.id, days=30
    )
    assert out["current_status"] == "operational"
    assert out["incidents"] == 1
    # 11 of 12 observed hours operational ≈ 91.667%
    assert out["uptime_pct"] == pytest.approx(11 / 12 * 100, abs=0.5)
    # Coverage is honest: 12h of a 30-day window
    assert out["coverage_pct"] == pytest.approx(12 / (30 * 24) * 100, abs=0.2)
    assert any(d["worst_status"] == "degraded" for d in out["daily"])


async def test_uptime_unknown_before_first_probe(db):
    model = await _mk_model(db, "NeverProbedGen")
    out = await AvailabilityService(db).uptime(
        entity_kind="model", entity_id=model.id, days=7
    )
    assert out["current_status"] == "unknown"
    assert out["uptime_pct"] is None  # never assumed-up
    assert out["incidents"] == 0
    assert out["daily"] == []

    with pytest.raises(AppError):
        await AvailabilityService(db).uptime(
            entity_kind="model", entity_id=model.id, days=0
        )

async def test_unknown_status_never_counts_as_uptime(db):
    """Mutation-audit killer: an 'unknown' probe interval is neither up nor
    down — it reduces coverage, never inflates uptime_pct."""
    model = await _mk_model(db, "UnknownGapGen")
    # 2h operational → 2h unknown → operational since 1h ago... simpler:
    db.add(_status(model.id, "operational", 4))
    db.add(_status(model.id, "unknown", 2))
    db.add(_status(model.id, "operational", 1))
    await db.flush()
    out = await AvailabilityService(db).uptime(
        entity_kind="model", entity_id=model.id, days=30
    )
    # observed = 2h up + 1h up = 3h; the 1h unknown gap is EXCLUDED
    assert out["uptime_pct"] == 100.0
    assert out["observed_seconds"] == pytest.approx(3 * 3600, rel=0.05)
