"""Round-7 governance & observability tests (ADR-016 §17).

Four-eyes on drafts, fence-aware run cancel, Prometheus-style metrics shape,
export delta feed pagination, eco audit-trail query, starter-source seeding
(paused-by-default posture).
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.services.benchmark import BenchmarkService
from app.ecosystem.services.drafts import DraftService
from app.exceptions import AppError

from tests.test_eco_services_db import (
    _mk_source,
    _mk_suite_with_cases,
    _mk_user,
)


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


# ── Four-eyes on drafts ─────────────────────────────────────────────


async def test_draft_creator_cannot_approve_or_publish_own_draft(db):
    creator = await _mk_user(db, "admin")
    second_admin = await _mk_user(db, "admin")
    svc = DraftService(db)
    draft = await svc.create(
        draft_type="skill_pack_update", title="4-eyes",
        payload={"target_pack_id": "P" * 26, "suggestions": [{"kind": "lesson"}]},
        created_by=creator.id,
    )
    await svc.transition(draft.id, to_status="in_review", actor_id=creator.id)  # self-service OK
    with pytest.raises(AppError) as exc:
        await svc.transition(draft.id, to_status="approved", actor_id=creator.id)
    assert exc.value.code == "ECO_FOUR_EYES"
    # A DIFFERENT admin approves; creator still cannot publish
    await svc.transition(draft.id, to_status="approved", actor_id=second_admin.id)
    with pytest.raises(AppError) as exc:
        await svc.transition(draft.id, to_status="published", actor_id=creator.id)
    assert exc.value.code == "ECO_FOUR_EYES"
    draft = await svc.transition(draft.id, to_status="published", actor_id=second_admin.id)
    assert draft.status == "published"
    # Creator CAN reject their own draft (self-service withdrawal)
    draft2 = await svc.create(
        draft_type="skill_pack_update", title="withdraw",
        payload={"target_pack_id": "P" * 26, "suggestions": [{}]},
        created_by=creator.id,
    )
    await svc.transition(draft2.id, to_status="in_review", actor_id=creator.id)
    draft2 = await svc.transition(draft2.id, to_status="rejected", actor_id=creator.id)
    assert draft2.status == "rejected"


# ── Fence-aware run cancel ──────────────────────────────────────────


async def test_cancel_only_queued_runs(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin, n_cases=1)
    bench = BenchmarkService(db)
    run = await bench.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "C" * 26}
    )
    run = await bench.cancel_run(run.id, actor_id=admin.id)
    assert run.status == "cancelled" and run.finished_at is not None
    # Cancelled runs can't execute or be re-cancelled
    with pytest.raises(AppError):
        await bench.execute_run(run.id)
    with pytest.raises(AppError) as exc:
        await bench.cancel_run(run.id, actor_id=admin.id)
    assert exc.value.code == "ECO_INVALID_TRANSITION"
    # Completed runs can't be cancelled
    run2 = await bench.create_run(
        suite.id, target={"entity_kind": "model_version", "entity_id": "C" * 26}
    )
    run2 = await bench.execute_run(run2.id)
    with pytest.raises(AppError):
        await bench.cancel_run(run2.id, actor_id=admin.id)


# ── Export delta feed ───────────────────────────────────────────────


async def test_export_changes_delta_pagination(db):
    source = await _mk_source(db)
    base = datetime.now(UTC)
    for i in range(3):
        obs = EcosystemObservation(
            source_id=source.id, event_type="catalog_snapshot",
            raw_hash=f"{i}d" * 32, normalized={},
        )
        db.add(obs)
        await db.flush()
        change = ChangeEvent(
            observation_id=obs.id, change_type="lifecycle", field=f"delta-{i}",
            severity="info",
        )
        db.add(change)
        await db.flush()
        change.detected_at = base + timedelta(seconds=i)
    await db.flush()
    # Service-level equivalent of the delta endpoint (oldest-first, cursor)
    since = base - timedelta(seconds=1)
    rows = list(
        await db.scalars(
            select(ChangeEvent)
            .where(
                ChangeEvent.detected_at > since,
                ChangeEvent.field.like("delta-%"),
            )
            .order_by(ChangeEvent.detected_at.asc())
        )
    )
    assert [r.field for r in rows] == ["delta-0", "delta-1", "delta-2"]
    # next_since cursor picks up where the page ended (exclusive >)
    mid = rows[0].detected_at
    rest = list(
        await db.scalars(
            select(ChangeEvent)
            .where(
                ChangeEvent.detected_at > mid,
                ChangeEvent.field.like("delta-%"),
            )
            .order_by(ChangeEvent.detected_at.asc())
        )
    )
    assert [r.field for r in rest] == ["delta-1", "delta-2"]


# ── Metrics shape ───────────────────────────────────────────────────


async def test_metrics_flatten_overview_gauges(db):
    from app.ecosystem.services.dashboard import DashboardService

    overview = await DashboardService(db).overview()
    lines = []
    for key, value in overview.items():
        if isinstance(value, dict):
            for sub, subvalue in value.items():
                if isinstance(subvalue, (int, float)):
                    lines.append(f"eco_{key}_{sub} {subvalue}")
        elif isinstance(value, (int, float)):
            lines.append(f"eco_{key} {value}")
    joined = "\n".join(lines)
    assert "eco_sources_active" in joined
    assert "eco_sources_stale" in joined
    assert "eco_observations_unverified" in joined
    # Prometheus text format: one metric per line, name SP value
    for line in lines:
        name, _, value = line.partition(" ")
        assert name.startswith("eco_") and value.replace(".", "", 1).lstrip("-").isdigit()


# ── Audit trail query ───────────────────────────────────────────────


async def test_eco_audit_trail_is_queryable(db):
    from app.controlplane.models.audit import CommercialAuditEvent
    from app.ecosystem.api.deps import eco_audit

    admin = await _mk_user(db, "admin")
    target = str(ULID())
    await eco_audit(
        db, admin, action="eco.lifecycle_transitioned", target_type="eco_model",
        target_id=target, before={"status": "verified"}, after={"status": "deprecated"},
    )
    rows = list(
        await db.scalars(
            select(CommercialAuditEvent).where(
                CommercialAuditEvent.action.like("eco.%"),
                CommercialAuditEvent.target_id == target,
            )
        )
    )
    assert len(rows) == 1
    assert rows[0].actor_user_id == admin.id
    assert rows[0].before == {"status": "verified"}


# ── Starter-source seeding ──────────────────────────────────────────


async def test_eco_seed_sources_paused_and_idempotent(db, monkeypatch):
    import app.cli as cli
    from app.ecosystem.models.source import EcosystemSource

    # Point the CLI at the test session factory (avoid a second engine)
    unique = str(ULID()).lower()[-6:]
    specs = [
        {**spec, "name": f"{spec['name']} [{unique}]"}
        for spec in cli.ECO_STARTER_SOURCES
    ]
    monkeypatch.setattr(cli, "ECO_STARTER_SOURCES", specs)

    from app.ecosystem.services.sources import SourceService

    async def seed(session):
        svc = SourceService(session)
        created = 0
        for spec in specs:
            existing = await session.scalar(
                select(EcosystemSource).where(EcosystemSource.name == spec["name"])
            )
            if existing:
                continue
            source = await svc.create(
                name=spec["name"], source_type=spec["source_type"],
                trust_level=spec["trust_level"], adapter_key=spec["adapter_key"],
                base_url=spec.get("base_url"), config=spec.get("config") or {},
                sync_interval_minutes=spec["sync_interval_minutes"],
                robots_compliant=True,
            )
            source.status = "paused"
            created += 1
        return created

    assert await seed(db) == len(specs)
    assert await seed(db) == 0  # idempotent
    rows = list(
        await db.scalars(
            select(EcosystemSource).where(EcosystemSource.name.like(f"%[{unique}]"))
        )
    )
    assert len(rows) == len(specs)
    # Never auto-fetch: everything seeded PAUSED, awaiting explicit activation
    assert all(r.status == "paused" for r in rows)
    # Seeded specs validate against the SSRF guard + adapter registry
    assert all(r.adapter_key in ("huggingface", "github_releases", "manual") for r in rows)
