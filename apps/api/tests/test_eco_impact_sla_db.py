"""Round-17 tests (ADR-016 §25): impact-analysis SLA escalation sweep."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.graph import ImpactAnalysis
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.worker import sweep_overdue_impacts
from app.models.notification import Notification
from tests.test_eco_services_db import _mk_source, _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_impact(db, *, deadline_delta_hours, status="open"):
    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="lifecycle_changed",
        raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
    )
    db.add(obs)
    await db.flush()
    change = ChangeEvent(
        observation_id=obs.id, change_type="lifecycle", field="sunset_at",
        severity="sunset_risk",
    )
    db.add(change)
    await db.flush()
    analysis = ImpactAnalysis(
        change_event_id=change.id, root_kind="model_version",
        root_id="0" * 26, classification="sunset",
        deadline_at=datetime.now(UTC) + timedelta(hours=deadline_delta_hours),
        status=status,
    )
    db.add(analysis)
    await db.flush()
    return analysis


async def test_overdue_open_impact_escalates_once_to_admins(db):
    admin = await _mk_user(db, "admin")
    overdue = await _mk_impact(db, deadline_delta_hours=-6)
    future = await _mk_impact(db, deadline_delta_hours=+6)
    resolved = await _mk_impact(db, deadline_delta_hours=-6, status="resolved")

    n = await sweep_overdue_impacts(db)
    assert n == 1  # only the open+overdue one
    await db.refresh(overdue)
    assert overdue.summary.get("escalated_at")
    assert overdue.status == "open"  # escalation never closes it
    notes = list(await db.scalars(
        select(Notification).where(
            Notification.user_id == admin.id,
            Notification.type == "ecosystem_impact_sla",
        )
    ))
    assert len(notes) == 1
    assert notes[0].data["impact_analysis_id"] == overdue.id

    # Idempotent: second sweep escalates nothing
    assert await sweep_overdue_impacts(db) == 0
    assert (future.summary or {}).get("escalated_at") is None
    assert (resolved.summary or {}).get("escalated_at") is None
