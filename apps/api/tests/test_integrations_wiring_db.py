"""P2b wiring tests — domain facts emit canonical mesh events (ADR-018 §12).

Covers the trigger_event mirror (legacy webhook events -> mesh, incl. the
ecosystem.change name map) and the directly-wired domain sites that are cheap
to drive (learner.enrolled, brief.created). The heavier sites
(project.approved, skill.completed, client.accepted) use the identical
fail-safe pattern and are exercised by their own service suites in the full
regression run.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
from app.integrations.models import IntegrationEvent
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db):
    u = User(
        email=f"wire-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Wire",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, user):
    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    tenant = await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )
    org = Organization(
        name=f"Org {ULID()}",
        slug=f"org-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    db.add(
        OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE)
    )
    await db.flush()
    return org


async def _mesh_events(db, org_id, event_type):
    return (
        (
            await db.execute(
                select(IntegrationEvent).where(
                    IntegrationEvent.org_id == org_id,
                    IntegrationEvent.type == event_type,
                )
            )
        )
        .scalars()
        .all()
    )


# ── trigger_event mirror ──


@pytest.mark.asyncio
async def test_trigger_event_mirrors_into_mesh(db):
    from app.services.webhook import WebhookService

    user = await _user(db)
    org = await _org(db, user)
    await WebhookService(db).trigger_event(org.id, "credential.issued", {"credential_id": "c1"})
    rows = await _mesh_events(db, org.id, "com.openskill.credential.issued.v1")
    assert len(rows) == 1
    assert rows[0].data == {"credential_id": "c1"}


@pytest.mark.asyncio
async def test_trigger_event_maps_ecosystem_change_name(db):
    from app.services.webhook import WebhookService

    user = await _user(db)
    org = await _org(db, user)
    await WebhookService(db).trigger_event(org.id, "ecosystem.change", {"change_id": "x"})
    assert len(await _mesh_events(db, org.id, "com.openskill.ecosystem.change_verified.v1")) == 1
    assert await _mesh_events(db, org.id, "com.openskill.ecosystem.change.v1") == []


@pytest.mark.asyncio
async def test_trigger_event_mirror_failsafe(db, monkeypatch):
    """A mesh failure must never break the business path (same posture as
    the legacy fire path)."""
    import app.integrations.facade as facade

    async def boom(*a, **k):
        raise RuntimeError("mesh down")

    monkeypatch.setattr(facade, "emit_event", boom)
    from app.services.webhook import WebhookService

    user = await _user(db)
    org = await _org(db, user)
    # Does not raise:
    await WebhookService(db).trigger_event(org.id, "credential.issued", {})


# ── learner.enrolled ──


@pytest.mark.asyncio
async def test_add_learner_emits_enrolled_but_staff_does_not(db):
    from app.models.cohort import CohortRole
    from app.services.cohort import CohortService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = CohortService(db)
    cohort = await svc.create_cohort(
        org_id=org.id, name=f"C {ULID()}", description=None, created_by=owner.id
    )
    learner = await _user(db)
    staff = await _user(db)
    for u in (learner, staff):
        db.add(
            OrgMember(org_id=org.id, user_id=u.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE)
        )
    await db.flush()
    member = await svc.add_member(cohort.id, learner.id, CohortRole.LEARNER, org.id)
    await svc.add_member(cohort.id, staff.id, CohortRole.INSTRUCTOR, org.id)
    rows = await _mesh_events(db, org.id, "com.openskill.learner.enrolled.v1")
    assert len(rows) == 1
    assert rows[0].subject == member.id
    assert rows[0].data == {"cohort_id": cohort.id, "user_id": learner.id}


# ── brief.created ──


@pytest.mark.asyncio
async def test_create_brief_emits_catalog_event(db):
    from app.services.client_brief import ClientBriefService

    user = await _user(db)
    org = await _org(db, user)
    brief = await ClientBriefService(db).create_brief(
        org_id=org.id,
        created_by=user.id,
        title=f"Brief {ULID()}",
        client_name="Acme",
        project_type="image",
        objective="Test objective",
    )
    rows = await _mesh_events(db, org.id, "com.openskill.brief.created.v1")
    assert len(rows) == 1
    assert rows[0].subject == brief.id
    # CRM-safe payload: ids/title/client/status only — no learner data.
    assert set(rows[0].data) == {"brief_id", "title", "client_name", "status"}


@pytest.mark.asyncio
async def test_invoice_finalized_routes_to_every_tenant_org_ids_only(db):
    """P10/R76: invoice.finalized mirrors into the mesh for EVERY org under
    the tenant, carrying ids only — never amounts (privacy boundary)."""
    from sqlalchemy import select as _select

    from app.controlplane.models.billing import Invoice
    from app.controlplane.services.billing import finalize_invoice
    from app.controlplane.services.tenants import Actor
    from app.integrations.models import IntegrationEvent

    owner = await _user(db)
    org = await _org(db, owner)
    tenant_id = org.tenant_id
    # Second org under the SAME tenant.
    org2 = Organization(
        name=f"Org2 {ULID()}",
        slug=f"o2-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant_id,
        created_by=owner.id,
    )
    db.add(org2)
    await db.flush()

    inv = Invoice(
        tenant_id=tenant_id,
        status="draft",
        currency="USD",
        subtotal_minor=12345,
        total_minor=12345,
        amount_due_minor=12345,
    )
    db.add(inv)
    await db.flush()
    await finalize_invoice(db, inv, actor=Actor(user_id=owner.id, type="platform"))
    await db.flush()

    events = (
        (
            await db.execute(
                _select(IntegrationEvent).where(
                    IntegrationEvent.subject == inv.id,
                    IntegrationEvent.type == "com.openskill.invoice.finalized.v1",
                )
            )
        )
        .scalars()
        .all()
    )
    assert {e.org_id for e in events} == {org.id, org2.id}
    for e in events:
        assert e.data == {"invoice_id": inv.id, "tenant_id": tenant_id}
        assert "12345" not in str(e.data)  # amounts never leak into the mesh


@pytest.mark.asyncio
async def test_fabric_tables_have_zero_model_migration_drift():
    """R369: the repo-wide `alembic check` fails on pre-existing drift in
    older epics' tables — fabric must not inherit that habit. Autogenerate
    comparison scoped to intg_* tables (and their indexes/constraints)
    must be EMPTY: every fabric model change ships with its migration."""
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    import app.controlplane.models  # noqa: F401 — cp_* registration (FK targets)
    import app.ecosystem.models  # noqa: F401
    import app.experiments.models  # noqa: F401
    import app.integrations.models  # noqa: F401
    import app.talent.models  # noqa: F401
    from app.core.database import engine
    from app.models import Base  # same aggregator migrations/env.py uses

    def _is_fabric(obj, name, type_, *_a, **_k):
        if type_ == "table":
            return bool(name and name.startswith("intg_"))
        table = getattr(obj, "table", None)
        tname = getattr(table, "name", "") or ""
        return tname.startswith("intg_")

    def _diffs(sync_conn):
        ctx = MigrationContext.configure(
            sync_conn,
            opts={"compare_type": True, "include_object": _is_fabric},
        )
        return compare_metadata(ctx, Base.metadata)

    async with engine.connect() as conn:
        diffs = await conn.run_sync(_diffs)
    await engine.dispose()
    assert not diffs, f"fabric model/migration drift: {diffs[:5]}"


@pytest.mark.asyncio
async def test_fabric_audit_row_actually_lands(db):
    """R384 (closes the R377 loop): record_fabric_audit is BEST-EFFORT — it
    swallows every failure with a log line, so 19 new call sites could all
    be silent no-ops and every structural guard would still pass. Prove a
    row LANDS: write the break-glass action for a real fabric org and read
    it back from cp_audit_events with the actor/target/payload intact."""
    from sqlalchemy import select as _select

    from app.controlplane.models.audit import CommercialAuditEvent
    from app.integrations.facade import record_fabric_audit

    user = await _user(db)
    org = await _org(db, user)

    await record_fabric_audit(
        db,
        org.id,
        user.id,
        "intg.break_glass.set",
        "user",
        user.id,
        after={"enabled": True},
    )
    await db.flush()

    row = (
        (
            await db.execute(
                _select(CommercialAuditEvent).where(
                    CommercialAuditEvent.action == "intg.break_glass.set",
                    CommercialAuditEvent.actor_user_id == user.id,
                )
            )
        )
        .scalars()
        .first()
    )
    assert row is not None, "audit write was silently swallowed"
    assert row.target_type == "user" and row.target_id == user.id
    assert row.after == {"enabled": True}
    assert row.tenant_id, "audit row lost its tenant scope"


@pytest.mark.asyncio
async def test_fabric_audit_fail_open_branches(db, monkeypatch):
    """R423: the two guard branches of record_fabric_audit had never
    executed. (1) actor None (system-initiated mutation) -> silent no-op,
    no row, no error. (2) the tenant lookup exploding -> swallowed with a
    warning, the caller's operation MUST NOT fail (best-effort contract,
    R377/R384)."""
    from sqlalchemy import select as _select

    from app.controlplane import facade as cp_facade
    from app.controlplane.models.audit import CommercialAuditEvent
    from app.integrations.facade import record_fabric_audit

    user = await _user(db)
    org = await _org(db, user)

    # (1) system actor: returns without touching the audit table.
    await record_fabric_audit(
        db, org.id, None, "intg.sweeper.ran", "connection", "none"
    )
    await db.flush()
    row = (
        (
            await db.execute(
                _select(CommercialAuditEvent).where(
                    CommercialAuditEvent.action == "intg.sweeper.ran"
                )
            )
        )
        .scalars()
        .first()
    )
    assert row is None

    # (2) tenant resolution explodes: swallowed, never propagates.
    async def boom(*a, **k):
        raise RuntimeError("tenant backend down")

    monkeypatch.setattr(cp_facade, "get_tenant_for_org", boom)
    await record_fabric_audit(
        db, org.id, user.id, "intg.break_glass.set", "user", user.id
    )  # must not raise
