"""Round-10 tests (ADR-016 §19): entity side-by-side compare + workload cost
estimator. Estimates are advisory — unpriced units flagged, never zeroed."""

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.mapping import PriceObservation
from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.services.catalog import CatalogService
from app.ecosystem.services.pricing import PricingService
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


async def _mk_model(db, name):
    model = AIModel(canonical_name=name, slug=f"{name.lower()}-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    return model


async def _mk_price(db, entity_id, unit, price, *, status="unreviewed"):
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="pricing_changed", entity_kind="model",
        external_ref=f"px-{str(ULID()).lower()}", raw_hash="p" * 64,
        normalized={"price": price, "unit": unit},
        canonical_entity_kind="model", canonical_entity_id=entity_id,
    )
    db.add(obs)
    await db.flush()
    row = PriceObservation(
        observation_id=obs.id, entity_kind="model", entity_id=entity_id,
        unit=unit, price=price, currency="USD", reconciliation_status=status,
    )
    db.add(row)
    await db.flush()
    return row


# ── Workload cost estimator ─────────────────────────────────────────


async def test_estimate_sorts_fully_priced_then_cheapest(db):
    cheap = await _mk_model(db, "CheapGen")
    pricey = await _mk_model(db, "PriceyGen")
    partial = await _mk_model(db, "PartialGen")
    await _mk_price(db, cheap.id, "token_input", 0.000001)
    await _mk_price(db, cheap.id, "token_output", 0.000002)
    await _mk_price(db, pricey.id, "token_input", 0.00001)
    await _mk_price(db, pricey.id, "token_output", 0.00002)
    await _mk_price(db, partial.id, "token_input", 0.0000001)  # missing output price

    rows = await PricingService(db).estimate(
        entity_kind="model",
        entity_ids=[pricey.id, partial.id, cheap.id],
        workload={"token_input": 1_000_000, "token_output": 200_000},
    )
    assert [r["entity_id"] for r in rows] == [cheap.id, pricey.id, partial.id]
    assert rows[0]["fully_priced"] and rows[1]["fully_priced"]
    assert rows[0]["estimated_total"] == pytest.approx(1.4)
    # Unpriced unit is FLAGGED, never silently zeroed
    assert rows[2]["fully_priced"] is False
    assert rows[2]["missing_units"] == ["token_output"]


async def test_estimate_prefers_approved_price_over_newer_observed(db):
    from datetime import UTC, datetime, timedelta

    model = await _mk_model(db, "ApprovedGen")
    older = await _mk_price(db, model.id, "token_input", 5.0, status="approved")
    newer = await _mk_price(db, model.id, "token_input", 1.0)  # newer but unreviewed
    # Explicit timestamps: same-transaction server defaults tie, which made
    # the ordering (and therefore this assertion) nondeterministic
    older.observed_at = datetime.now(UTC) - timedelta(days=2)
    newer.observed_at = datetime.now(UTC)
    # A rejected price must never win, however new it is
    rejected = await _mk_price(db, model.id, "token_input", 0.001, status="rejected")
    rejected.observed_at = datetime.now(UTC) + timedelta(minutes=1)
    await db.flush()

    rows = await PricingService(db).estimate(
        entity_kind="model", entity_ids=[model.id], workload={"token_input": 2},
    )
    assert rows[0]["estimated_total"] == pytest.approx(10.0)
    assert rows[0]["all_prices_approved"] is True

    # Rejected must be excluded even with NO approved competitor: only the
    # unreviewed 1.0 remains eligible on a fresh entity
    from datetime import UTC, datetime, timedelta

    lone = await _mk_model(db, "LoneGen")
    ok_price = await _mk_price(db, lone.id, "token_input", 1.0)
    ok_price.observed_at = datetime.now(UTC) - timedelta(hours=1)
    bad = await _mk_price(db, lone.id, "token_input", 0.001, status="rejected")
    bad.observed_at = datetime.now(UTC)
    await db.flush()
    rows = await PricingService(db).estimate(
        entity_kind="model", entity_ids=[lone.id], workload={"token_input": 2},
    )
    assert rows[0]["estimated_total"] == pytest.approx(2.0)  # 1.0×2, never 0.001


async def test_estimate_rejects_unknown_unit_and_bad_quantity(db):
    model = await _mk_model(db, "BadInputGen")
    with pytest.raises(AppError) as exc:
        await PricingService(db).estimate(
            entity_kind="model", entity_ids=[model.id], workload={"gpu_hour": 1},
        )
    assert exc.value.code == "VALIDATION_ERROR"
    with pytest.raises(AppError):
        await PricingService(db).estimate(
            entity_kind="model", entity_ids=[model.id], workload={"token_input": -1},
        )


# ── Side-by-side compare ────────────────────────────────────────────


async def test_compare_entities_returns_facts_prices_and_uniform_404(db):
    a = await _mk_model(db, "AlphaGen")
    b = await _mk_model(db, "BetaGen")
    await _mk_price(db, a.id, "image", 0.04, status="approved")

    out = await CatalogService(db).compare_entities("model", [a.id, b.id])
    assert [r["canonical_name"] for r in out] == ["AlphaGen", "BetaGen"]
    assert out[0]["prices"]["image"]["approved"] is True
    assert out[1]["prices"] == {}
    assert out[0]["benchmark"] is None  # never benchmarked

    # Bounds + uniform 404 (no existence oracle)
    with pytest.raises(AppError) as exc:
        await CatalogService(db).compare_entities("model", [a.id])
    assert exc.value.code == "VALIDATION_ERROR"
    with pytest.raises(AppError) as exc:
        await CatalogService(db).compare_entities("model", [a.id, "0" * 26])
    assert exc.value.status_code == 404

async def test_price_history_series_and_trend(db):
    from datetime import UTC, datetime, timedelta

    from app.ecosystem.services.pricing import PricingService

    model = await _mk_model(db, "TrendGen")
    base = datetime.now(UTC) - timedelta(days=10)
    for day, price in [(0, 10.0), (5, 8.0), (10, 6.0)]:
        row = await _mk_price(db, model.id, "image", price)
        row.observed_at = base + timedelta(days=day)
    rejected = await _mk_price(db, model.id, "image", 999.0, status="rejected")
    rejected.observed_at = base + timedelta(days=11)
    await db.flush()

    out = await PricingService(db).history(entity_kind="model", entity_id=model.id)
    points = out["series"]["image"]
    assert [p["price"] for p in points] == [10.0, 8.0, 6.0]  # oldest first, rejected excluded
    trend = out["trends"]["image"]
    assert trend is not None
    assert trend["slope"] < 0  # falling price
    # Unknown unit rejected; unit filter works
    with pytest.raises(AppError):
        await PricingService(db).history(
            entity_kind="model", entity_id=model.id, unit="gpu_hour"
        )
    only = await PricingService(db).history(
        entity_kind="model", entity_id=model.id, unit="token_input"
    )
    assert only["series"] == {}
