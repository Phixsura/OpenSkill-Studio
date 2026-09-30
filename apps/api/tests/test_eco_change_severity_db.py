"""Round-57 killers (ADR-016 §56): severity classification + auto fan-out."""

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.services.change_detection import detect_changes
from tests.test_eco_services_db import _mk_source


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _obs(db, source, ref, normalized, entity_id=None):
    obs = EcosystemObservation(
        source_id=source.id, event_type="catalog_snapshot", entity_kind="model",
        external_ref=ref, raw_hash=(str(ULID()).lower() * 3)[:64],
        normalized=normalized, canonical_entity_kind="model" if entity_id else None,
        canonical_entity_id=entity_id,
    )
    db.add(obs)
    await db.flush()
    return obs


async def test_sunset_field_change_is_sunset_risk(db):
    """Killer: a sunset_at appearing on a tracked entity is sunset_risk —
    never demoted to info (deprecation calendars, watch alerts, iCal feed
    all key off this severity)."""
    source = await _mk_source(db)
    ref = f"sun-{str(ULID()).lower()[:8]}"
    await _obs(db, source, ref, {"sunset_at": None})
    obs2 = await _obs(db, source, ref, {"sunset_at": "2026-12-31T00:00:00Z"})
    await detect_changes(db, obs2)
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.observation_id == obs2.id, ChangeEvent.field == "sunset_at"
        )
    )
    assert change is not None
    assert change.severity == "sunset_risk"


async def test_high_severity_changes_auto_enqueue_impact(db):
    """Killer: breaking/security/sunset changes on a RESOLVED entity must
    auto-enqueue impact analysis (Dependabot lesson: new advisory → rescan
    dependents, always) — an emptied fan-out set silently disables this."""
    source = await _mk_source(db)
    model = AIModel(canonical_name=f"FanGen-{str(ULID()).lower()[:6]}", slug=f"fg-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    ref = f"fan-{str(ULID()).lower()[:8]}"
    await _obs(db, source, ref, {"license": "MIT"}, entity_id=model.id)
    obs2 = await _obs(db, source, ref, {"license": "BUSL-1.1"}, entity_id=model.id)
    await detect_changes(db, obs2)
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.observation_id == obs2.id, ChangeEvent.field == "license"
        )
    )
    assert change is not None and change.severity == "breaking"
    from app.controlplane.models.outbox import OutboxMessage

    msg = await db.scalar(
        select(OutboxMessage).where(
            OutboxMessage.topic == "eco.compute_impact",
            OutboxMessage.payload["change_event_id"].as_string() == change.id,
        )
    )
    assert msg is not None  # impact enqueued without any operator click


async def test_price_magnitude_sign_matches_direction(db):
    """Killer: a price INCREASE must carry a POSITIVE change_pct — a flipped
    sign would tell operators a 50% hike was a 50% cut."""
    source = await _mk_source(db)
    ref = f"pm-{str(ULID()).lower()[:8]}"
    await _obs(db, source, ref, {"pricing": [{"unit": "image", "price": 0.04}]})
    obs2 = await _obs(db, source, ref, {"pricing": [{"unit": "image", "price": 0.06}]})
    await detect_changes(db, obs2)
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.observation_id == obs2.id, ChangeEvent.field == "pricing"
        )
    )
    assert change is not None
    assert change.severity == "update_available"  # increase escalates
    magnitude = (change.new_value or {}).get("magnitude")
    assert magnitude is not None
    assert magnitude["change_pct"] == 50.0  # +50%, positive sign

async def test_impact_depth_cap_truncates_at_six(db):
    """Mutation-audit killer: the blast-radius walk stops at IMPACT_MAX_DEPTH
    — an unbounded cap would let one sunset event walk the entire graph."""
    from app.ecosystem.models.graph import DependencyEdge
    from app.ecosystem.services.impact import ImpactService

    tag = str(ULID()).lower()[:6]
    # chain: n0 <- n1 <- ... <- n8 (each depends on the previous)
    ids = [f"{i:02d}" + "c" * 22 + tag[:2] for i in range(9)]
    for i in range(1, 9):
        db.add(DependencyEdge(
            from_kind="component", from_id=ids[i],
            to_kind="component", to_id=ids[i - 1],
            constraint_type="uses",
        ))
    await db.flush()
    items, _truncated = await ImpactService(db)._traverse("component", ids[0])
    depths = {node_id: depth for (_k, node_id), (depth, _p) in items.items()}
    assert max(depths.values()) <= 6
    assert ids[6] in depths          # depth 6 still reached
    assert ids[7] not in depths      # depth 7 pruned by the cap
    assert ids[8] not in depths

def test_version_range_unparseable_bound_fails_open():
    """Round-110 killer: an unparseable BOUND in a comparison token must
    return None (cannot rule out — advisory keeps the entity), never False
    ("provably safe"). A '2.O' typo in a CVE range must not hide the hit."""
    from app.ecosystem.services.stats import version_in_range

    for expr in (">=1.0 <2.O", ">=x", "<=beta", ">nope", "==v?"):
        assert version_in_range("1.5.0", expr) is None, expr
    # Sanity: well-formed ranges still decide
    assert version_in_range("1.5.0", ">=1.0 <2.0") is True
    assert version_in_range("2.5.0", ">=1.0 <2.0") is False

def test_version_range_operator_semantics():
    """Round-110b killers ×6: pin every operator's boundary semantics —
    advisories and impact analyses depend on these being exact."""
    from app.ecosystem.services.stats import version_in_range

    # caret: >=lower (inclusive) <next-major (exclusive)
    assert version_in_range("1.2.3", "^1.2.3") is True   # lower bound inclusive
    assert version_in_range("1.9.9", "^1.2.3") is True
    assert version_in_range("2.0.0", "^1.2.3") is False  # upper bound exclusive
    # tilde: >=lower <next-minor
    assert version_in_range("1.2.9", "~1.2.3") is True
    assert version_in_range("1.3.0", "~1.2.3") is False
    # comparison boundaries
    assert version_in_range("1.0.0", ">=1.0.0") is True   # >= includes equal
    assert version_in_range("2.0.0", "<2.0.0") is False   # < excludes equal
    assert version_in_range("2.0.0", "<=2.0.0") is True
    assert version_in_range("1.0.0", ">1.0.0") is False
    # short versions pad with ZEROS: '1.2' == '1.2.0'
    assert version_in_range("1.2.0", "==1.2") is True
    assert version_in_range("1.2.9", "==1.2") is False
    # bare token is exact match
    assert version_in_range("1.2.0", "1.2.0") is True
    assert version_in_range("1.2.1", "1.2.0") is False
