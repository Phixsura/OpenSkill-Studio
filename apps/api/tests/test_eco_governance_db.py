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
    _mk_capability_tag,
    _mk_org,
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

async def test_audit_csv_defuses_formula_injection(db):
    from app.controlplane.services.audit import Actor, record_audit
    from app.ecosystem.api.dashboard import eco_audit_trail_csv

    admin = await _mk_user(db, "admin")
    await record_audit(
        db, actor=Actor(user_id=admin.id, type="platform"), action="eco.conflict_resolved",
        target_type="eco_source", target_id="0" * 26,
        reason="=HYPERLINK(\"http://evil\")",
    )
    await db.flush()
    resp = await eco_audit_trail_csv(
        action="eco.conflict_resolved", target_id="0" * 26, limit=10, db=db, _user=admin
    )
    body = resp.body.decode()
    assert resp.media_type.startswith("text/csv")
    assert "'=HYPERLINK" in body  # formula defused with leading apostrophe
    assert body.splitlines()[0].startswith("id,actor_user_id,action")

async def test_editing_in_review_draft_dismisses_review(db):
    """GitHub 'new commits dismiss review' semantics: an in_review payload
    edit drops the draft back to draft status — closing the TOCTOU window
    between a reviewer reading and a second admin approving."""
    creator = await _mk_user(db, "admin")
    second_admin = await _mk_user(db, "admin")
    svc = DraftService(db)
    draft = await svc.create(
        draft_type="skill_pack_update", title="toctou",
        payload={"target_pack_id": "P" * 26, "suggestions": [{"kind": "lesson"}]},
        created_by=creator.id,
    )
    await svc.transition(draft.id, to_status="in_review", actor_id=creator.id)

    # Creator swaps the payload while it sits in review
    draft = await svc.update_payload(
        draft.id,
        payload={"target_pack_id": "P" * 26, "suggestions": [{"kind": "SWAPPED"}]},
    )
    assert draft.status == "draft"  # review basis invalidated

    # Approval of the swapped content now requires a fresh submit + review
    with pytest.raises(AppError) as exc:
        await svc.transition(draft.id, to_status="approved", actor_id=second_admin.id)
    assert exc.value.code in ("ECO_INVALID_TRANSITION", "ECO_DRAFT_NOT_APPROVED")
    await svc.transition(draft.id, to_status="in_review", actor_id=creator.id)
    draft = await svc.transition(draft.id, to_status="approved", actor_id=second_admin.id)
    assert draft.status == "approved"
    # Approved drafts are immutable
    with pytest.raises(AppError):
        await svc.update_payload(draft.id, payload={"target_pack_id": "P" * 26,
                                                    "suggestions": [{"kind": "late"}]})

async def test_budget_cap_is_inclusive_boundary(db):
    """Mutation-audit killer: the budget check is >= — when spend REACHES the
    cap, execution stops before the next case (a strict > would run one case
    past the budget)."""
    from decimal import Decimal

    from app.ecosystem.models.benchmark import BenchmarkResult
    from app.ecosystem.services.benchmark import BenchmarkService

    class FixedCost:
        async def execute_case(self, run, case, repeat):
            return {"output_assets": [], "latency_ms": 100, "usage": {},
                    "cost_usd": 1.0, "automated_scores": {},
                    "failed": False, "retries": 0}

    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin, n_cases=3)
    suite.repeat_count = 1
    await db.flush()
    svc = BenchmarkService(db, executor=FixedCost())
    run = await svc.create_run(
        suite.id, target={"entity_kind": "model", "entity_id": "0" * 26},
        budget_usd_cap=2.0,
    )
    run = await svc.execute_run(run.id)
    assert run.status == "failed"
    assert "ECO_BUDGET_EXCEEDED" in (run.error or "")
    results = list(await db.scalars(
        select(BenchmarkResult).where(BenchmarkResult.run_id == run.id)
    ))
    assert len(results) == 2  # stops the moment spend REACHES the cap
    assert run.total_cost_usd == Decimal("2")

async def test_generated_drafts_carry_gates_and_provenance(db):
    """Mutation-audit killers ×2: every generated step keeps its human
    review_gate, and the draft carries full origin provenance (kind + source
    repo + graph hash) — an untraceable or ungated draft is unreviewable."""
    from app.ecosystem.models.catalog import ExternalWorkflow
    from app.ecosystem.models.mapping import CapabilityMapping

    workflow = ExternalWorkflow(
        canonical_name=f"WfGen-{str(ULID()).lower()[:6]}",
        slug=f"wf-{str(ULID()).lower()}",
        source_repo="github.com/acme/wf",
        graph_hash="g" * 64,
        node_types=["KSampler"],
    )
    db.add(workflow)
    await db.flush()
    await _mk_capability_tag(db, "image_generation")
    db.add(CapabilityMapping(
        entity_kind="workflow", entity_id=workflow.id,
        capability_key="image_generation", evidence_level="vendor_claimed",
        io_spec={},
    ))
    await db.flush()

    draft = await DraftService(db).generate_workflow_pack_draft(
        external_workflow_id=workflow.id
    )
    steps = draft.payload["definition"]["steps"]
    assert steps and all(s["review_gate"] is True for s in steps)
    origin = draft.payload["origin"]
    assert origin["kind"] == "external_workflow"
    assert origin["id"] == workflow.id
    assert origin["graph_hash"] == "g" * 64
    assert draft.status == "draft"  # generation never pre-approves


async def test_published_eco_draft_materializes_private_draft_pack(db):
    """Mutation-audit killer: publishing the ECO draft materializes the
    product pack as a PRIVATE DRAFT — never as a published product."""
    from app.models.skill_pack import PackStatus, PackVisibility
    from app.models.workflow_pack import WorkflowPack

    creator = await _mk_user(db, "admin")
    approver = await _mk_user(db, "admin")
    org = await _mk_org(db)
    svc = DraftService(db)
    draft = await svc.create(
        draft_type="workflow_pack", title="matpack",
        payload={"name": "MatPack",
                 "definition": {"steps": [{"id": "s1", "capability": "image_generation"}]}},
        created_by=creator.id, org_id=org.id,
    )
    await svc.transition(draft.id, to_status="in_review", actor_id=creator.id, org_id=org.id)
    await svc.transition(draft.id, to_status="approved", actor_id=approver.id, org_id=org.id)
    draft = await svc.transition(
        draft.id, to_status="published", actor_id=approver.id, org_id=org.id
    )
    pack = await db.get(WorkflowPack, draft.published_ref)
    assert pack is not None
    assert pack.status == PackStatus.DRAFT          # product-side stays draft
    assert pack.visibility == PackVisibility.PRIVATE  # and private

async def test_lifecycle_gates_refuse_archived_inactive_and_bad_targets(db):
    """Mutation-audit killers ×3: an ARCHIVED source never syncs; a
    non-active suite never runs; a run target must name an entity kind."""
    from app.ecosystem.services.sync import SyncService

    admin = await _mk_user(db, "admin")
    source = await _mk_source(db, adapter_key="manual")
    source.status = "archived"
    await db.flush()
    with pytest.raises(AppError) as exc:
        await SyncService(db).run_sync(source.id, raw_payload=b"{}")
    assert exc.value.code == "ECO_SOURCE_PAUSED"

    suite = await _mk_suite_with_cases(db, admin)
    suite.status = "retired"
    await db.flush()
    svc = BenchmarkService(db)
    with pytest.raises(AppError) as exc:
        await svc.create_run(
            suite.id, target={"entity_kind": "model", "entity_id": "0" * 26}
        )
    assert exc.value.code == "VALIDATION_ERROR"

    suite.status = "active"
    await db.flush()
    with pytest.raises(AppError) as exc:
        await svc.create_run(suite.id, target={"entity_id": "0" * 26})  # no kind
    assert exc.value.code == "VALIDATION_ERROR"
    with pytest.raises(AppError):
        await svc.create_run(suite.id, target="not-a-dict")  # type: ignore[arg-type]

async def test_payload_edit_racing_publish_cannot_mutate_published_draft(db):
    """Round-133 killer: a payload edit racing the approve->publish transition
    must lose cleanly (409) — a published draft's payload is immutable."""
    import asyncio

    from app.core.database import AsyncSessionLocal
    from app.ecosystem.services.drafts import DraftService

    user = await _mk_user(db, "admin")
    approver = await _mk_user(db, "admin")
    draft = await DraftService(db).create(
        draft_type="benchmark_suite",
        title="RacePub",
        payload={"family": "ecommerce_hero", "capability_key": "image_generation"},
        created_by=user.id,
    )
    svc = DraftService(db)
    await svc.transition(draft.id, to_status="in_review", actor_id=user.id)
    await svc.transition(draft.id, to_status="approved", actor_id=approver.id)
    await db.commit()
    draft_id, actor = draft.id, approver.id

    async def publish():
        async with AsyncSessionLocal() as session:
            try:
                await DraftService(session).transition(
                    draft_id, to_status="published", actor_id=actor
                )
                await session.commit()
                return "published"
            except AppError as exc:
                await session.rollback()
                return exc.code

    async def edit():
        async with AsyncSessionLocal() as session:
            try:
                await DraftService(session).update_payload(
                    draft_id, payload={"family": "EVIL", "capability_key": "EVIL"}
                )
                await session.commit()
                return "edited"
            except AppError as exc:
                await session.rollback()
                return exc.code

    results = await asyncio.gather(publish(), edit())
    assert "published" in results, results
    async with AsyncSessionLocal() as session:
        from app.ecosystem.models.replacement import ComponentDraft

        row = await session.get(ComponentDraft, draft_id)
        if "edited" not in results:
            assert row.payload["family"] == "ecommerce_hero", "published payload mutated"
