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
    await WebhookService(db).trigger_event(
        org.id, "credential.issued", {"credential_id": "c1"}
    )
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
