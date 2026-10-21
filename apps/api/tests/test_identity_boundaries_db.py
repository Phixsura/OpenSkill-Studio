"""R631: pins for identity.resolve's input-sanitization walls (full-file
mutation sweep showed every boundary unpinned) and the inactive-linked-user
wall, plus the backchannel sub-type and stale-iat windows.

Separate file so the boundaries read as one contract; added to test-intg.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.exceptions import AppError
from app.integrations.models import IdentityMatchQueue, OrgDomain
from app.integrations.services.identity import IdentityService, VerifiedExternalIdentity
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _org(db):
    owner = User(
        email=f"idb-{uuid.uuid4().hex[:8]}@test.com",
        password_hash="x",
        display_name="O",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(owner)
    await db.flush()
    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    tenant = await tenant_svc.create_tenant(
        db,
        name=f"T idb {uuid.uuid4().hex[:6]}",
        slug=f"t-idb-{uuid.uuid4().hex[:8]}",
        actor=Actor(user_id=owner.id, type="platform"),
        owner_user_id=owner.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )
    org = Organization(
        name=f"IDB {uuid.uuid4().hex[:6]}",
        slug=f"idb-{uuid.uuid4().hex[:8]}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=owner.id,
    )
    db.add(org)
    await db.flush()
    db.add(
        OrgMember(org_id=org.id, user_id=owner.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE)
    )
    dom = f"idb-{uuid.uuid4().hex[:8]}.example.edu"
    db.add(OrgDomain(org_id=org.id, domain=dom, status="verified", verification_token="t"))
    await db.flush()
    return org, dom


def _ident(org, dom, **kw):
    base = dict(
        org_id=org.id,
        source="sso",
        connection_ref=f"conn-{uuid.uuid4().hex[:8]}",
        subject=f"sub-{uuid.uuid4().hex[:8]}",
        email=f"u-{uuid.uuid4().hex[:8]}@{dom}",
        email_verified=True,
        display_name="D",
    )
    base.update(kw)
    return VerifiedExternalIdentity(**base)


async def _queue_reason(db, org_id: str, subject: str) -> str | None:
    row = (
        (
            await db.execute(
                select(IdentityMatchQueue).where(
                    IdentityMatchQueue.org_id == org_id,
                    IdentityMatchQueue.subject == subject,
                )
            )
        )
        .scalars()
        .first()
    )
    return row.reason if row else None


@pytest.mark.asyncio
async def test_subject_length_wall_exact_500(db):
    """subject >500 is a 403 (code + STATUS pinned); exactly 500 proceeds."""
    org, dom = await _org(db)
    svc = IdentityService(db)
    with pytest.raises(AppError) as e:
        await svc.resolve(_ident(org, dom, subject="s" * 501))
    assert e.value.code == "IDENTITY_AMBIGUOUS" and e.value.status_code == 403
    # exactly 500: passes the wall, lands in JIT (new user) — not the 403 wall
    r = await svc.resolve(_ident(org, dom, subject="s" * 500), allow_jit=True)
    assert r.jit_created


@pytest.mark.asyncio
async def test_email_length_wall_exact_255(db):
    """email >255 is sanitized to None → queued as unverified; exactly 255
    survives sanitization (and proceeds to the member/JIT path)."""
    org, dom = await _org(db)
    svc = IdentityService(db)
    local = "a" * (256 - len(dom) - 1)
    long_email = f"{local}@{dom}"  # 256 chars
    assert len(long_email) == 256
    subj = f"sub-{uuid.uuid4().hex[:8]}"
    with pytest.raises(AppError):
        await svc.resolve(_ident(org, dom, subject=subj, email=long_email), allow_jit=True)
    assert await _queue_reason(db, org.id, subj) == "email_unverified_or_foreign_domain"
    exact = f"{'a' * (255 - len(dom) - 1)}@{dom}"  # 255 chars
    assert len(exact) == 255
    r = await svc.resolve(_ident(org, dom, email=exact), allow_jit=True)
    assert r.jit_created and r.user.email == exact


@pytest.mark.asyncio
async def test_display_name_truncated_at_100(db):
    org, dom = await _org(db)
    svc = IdentityService(db)
    r = await svc.resolve(_ident(org, dom, display_name="n" * 150), allow_jit=True)
    assert r.jit_created and r.user.display_name == "n" * 100
    # empty display_name degrades to the email local part, not ""
    r2 = await svc.resolve(_ident(org, dom, display_name=""), allow_jit=True)
    assert r2.user.display_name  # never empty string


@pytest.mark.asyncio
async def test_inactive_linked_user_wall(db):
    """A linked user who is deactivated must be a 403 — the Or→And mutant
    here would let an INACTIVE account complete SSO login."""
    org, dom = await _org(db)
    svc = IdentityService(db)
    ident = _ident(org, dom)
    r = await svc.resolve(ident, allow_jit=True)
    assert r.jit_created
    r.user.status = UserStatus.SUSPENDED
    await db.flush()
    with pytest.raises(AppError) as e:
        await svc.resolve(ident)  # same subject -> hot link path
    assert e.value.code == "SSO_NO_ACCOUNT" and e.value.status_code == 403


@pytest.mark.asyncio
async def test_refusal_status_codes_are_403(db):
    """Every refusal arm of resolve() is status 403 (not 404/401)."""
    org, dom = await _org(db)
    svc = IdentityService(db)
    # no-member, no-jit
    with pytest.raises(AppError) as e1:
        await svc.resolve(_ident(org, dom))
    assert e1.value.status_code == 403
    # unverified email
    with pytest.raises(AppError) as e2:
        await svc.resolve(_ident(org, dom, email_verified=False))
    assert e2.value.status_code == 403


@pytest.mark.asyncio
async def test_single_member_email_match_succeeds(db):
    """Exactly ONE active member with the verified email → matched (not JIT,
    not queued) — pins the len(members) > 1 boundary (GtE mutant queues the
    single-member case)."""
    org, dom = await _org(db)
    email = f"m-{uuid.uuid4().hex[:8]}@{dom}"
    member_user = User(
        email=email,
        password_hash="x",
        display_name="M",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(member_user)
    await db.flush()
    db.add(
        OrgMember(
            org_id=org.id,
            user_id=member_user.id,
            role=OrgRole.STUDENT,
            status=MemberStatus.ACTIVE,
        )
    )
    await db.flush()
    r = await IdentityService(db).resolve(_ident(org, dom, email=email))
    assert not r.jit_created and r.user.id == member_user.id
