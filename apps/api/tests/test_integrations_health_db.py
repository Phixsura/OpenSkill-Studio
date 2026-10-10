"""R36 — fabric health summary endpoint (aggregate counts only)."""

import uuid

import pytest
import pytest_asyncio
from ulid import ULID

from app.core.security import hash_password
from app.integrations.api.connections import fabric_health
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
        email=f"hl-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Health",
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
        name=f"Org {ULID()}", slug=f"o-{str(ULID()).lower()}", status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
    )
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.OWNER,
                     status=MemberStatus.ACTIVE))
    await db.flush()
    return org


@pytest.mark.asyncio
async def test_health_counts_are_org_scoped(db):
    from app.integrations.services.connections import ConnectionService
    from app.models.webhook import WebhookSubscription

    owner = await _user(db)
    org = await _org(db, owner)
    other_owner = await _user(db)
    other = await _org(db, other_owner)

    csvc = ConnectionService(db)
    await csvc.sync_provider_catalog()
    await db.flush()
    await csvc.create(
        org.id, provider_key="generic_webhook", name=f"h-{uuid.uuid4().hex[:6]}",
        config={}, base_url="https://x.example.com", created_by=owner.id,
    )
    # Noise in ANOTHER org must not leak into this org's counts.
    await csvc.create(
        other.id, provider_key="generic_webhook", name=f"h-{uuid.uuid4().hex[:6]}",
        config={}, base_url="https://y.example.com", created_by=other_owner.id,
    )
    db.add(WebhookSubscription(
        org_id=org.id, url="https://sink.example.com/h", events=["project.approved"],
        secret="whsec_x", active=False,
    ))
    await db.flush()

    out = await fabric_health(org.id, db=db, user=owner)
    data = out["data"]
    assert data["connections"]["total"] == 1
    assert data["connections"]["by_status"] == {"pending": 1}
    assert data["subscriptions"] == {"total": 1, "disabled": 1}
    assert data["deliveries"] == {"pending": 0, "exhausted_24h": 0}
    assert data["identity_queue_pending"] == 0
    assert data["sync"] == {"profiles": 0, "failed_runs_24h": 0}
    assert data["sso_connections_active"] == 0

    # Non-admin of the org is refused (uniform wall).
    from fastapi.exceptions import HTTPException

    with pytest.raises(HTTPException):
        await fabric_health(org.id, db=db, user=other_owner)
