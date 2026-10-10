"""P6 tests — roster provisioning (staged -> Cohort/CohortMember with
conflict reporting) and the OneRoster connector against a faked SIS."""

import uuid
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.models import (
    IdentityMatchQueue,
    StagedRecord,
)
from app.integrations.services.roster import RosterProvisioningService
from app.models.cohort import Cohort, CohortMember, CohortRole
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
    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    u = User(
        email=f"ro-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Ro",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    tenant = await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t-{str(ULID()).lower()}",
        actor=Actor(user_id=u.id, type="platform"),
        owner_user_id=u.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )
    org = Organization(
        name=f"Org {ULID()}",
        slug=f"org-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=u.id,
    )
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=u.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE))
    await db.flush()
    return org, u


async def _conn(db, org, owner):
    from app.integrations.services.connections import ConnectionService

    svc = ConnectionService(db)
    await svc.sync_provider_catalog()
    await db.flush()
    conn = await svc.create(
        org.id,
        provider_key="oneroster",
        name=f"sis-{uuid.uuid4().hex[:8]}",
        config={"token_url": "https://sis.example.com/token"},
        base_url="https://sis.example.com/ims/oneroster/rostering/v1p2",
        created_by=owner.id,
    )
    conn.status = "active"
    await db.flush()
    return conn


def _stage(db, conn, model, external_id, payload, status="active"):
    db.add(
        StagedRecord(
            connection_id=conn.id,
            model=model,
            external_id=external_id,
            payload=payload,
            raw_hash=f"h-{external_id}",
            status=status,
        )
    )


async def _domain(db, org, domain):
    from datetime import UTC, datetime

    from app.integrations.models import OrgDomain

    db.add(
        OrgDomain(
            org_id=org.id,
            domain=domain,
            status="verified",
            verification_token="t",
            verified_at=datetime.now(UTC),
        )
    )
    await db.flush()


# ── provisioning ──


@pytest.mark.asyncio
async def test_provision_classes_enrollments_full_path(db):
    org, owner = await _org(db)
    await _domain(db, org, "school.example.edu")
    conn = await _conn(db, org, owner)
    # Existing member matched by email; one JIT user; one teacher.
    alice = await _user_member(db, org, "alice@school.example.edu")
    _stage(db, conn, "roster.class", "c-1", {"title": "AI Studio 101"})
    _stage(db, conn, "roster.user", "u-alice", {"email": "alice@school.example.edu"})
    _stage(db, conn, "roster.user", "u-new", {"email": "newkid@school.example.edu"})
    _stage(db, conn, "roster.user", "u-teach", {"email": "teach@school.example.edu"})
    _stage(
        db, conn, "roster.enrollment", "e-1",
        {"class_external_id": "c-1", "user_external_id": "u-alice", "role": "student"},
    )
    _stage(
        db, conn, "roster.enrollment", "e-2",
        {"class_external_id": "c-1", "user_external_id": "u-new", "role": "student"},
    )
    _stage(
        db, conn, "roster.enrollment", "e-3",
        {"class_external_id": "c-1", "user_external_id": "u-teach", "role": "teacher"},
    )
    await db.flush()

    report = await RosterProvisioningService(db).provision(
        org.id, conn.id, actor_id=owner.id, options={"jit_users": True}
    )
    assert report["cohorts_created"] == 1
    assert report["members_added"] == 3
    assert report["conflicts"] == 0

    cohort = (
        await db.execute(
            select(Cohort).where(Cohort.org_id == org.id, Cohort.name == "AI Studio 101")
        )
    ).scalar_one()
    assert (cohort.settings["integration"]) == {
        "connection_id": conn.id,
        "external_id": "c-1",
    }
    members = (
        await db.execute(select(CohortMember).where(CohortMember.cohort_id == cohort.id))
    ).scalars().all()
    assert len(members) == 3
    roles = {m.user_id: m.role for m in members}
    assert roles[alice.id] == CohortRole.LEARNER
    # teacher mapped to INSTRUCTOR
    assert CohortRole.INSTRUCTOR in roles.values()
    # JIT user provisioned as org student
    new_user = (
        await db.execute(select(User).where(User.email == "newkid@school.example.edu"))
    ).scalar_one()
    assert new_user.email_verified is True

    # Re-provision is idempotent: nothing added twice.
    report2 = await RosterProvisioningService(db).provision(
        org.id, conn.id, actor_id=owner.id, options={"jit_users": True}
    )
    assert report2["members_added"] == 0 and report2["cohorts_created"] == 0


async def _user_member(db, org, email):
    u = User(
        email=email,
        password_hash=hash_password("Test123!"),
        display_name=email.split("@")[0],
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=u.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE))
    await db.flush()
    return u


@pytest.mark.asyncio
async def test_provision_conflicts_skip_never_guess(db):
    org, owner = await _org(db)
    await _domain(db, org, "sch2.example.edu")
    conn = await _conn(db, org, owner)
    _stage(db, conn, "roster.class", "c-ok", {"title": "OK Class"})
    # enrollment -> unknown class
    _stage(
        db, conn, "roster.enrollment", "e-dangling",
        {"class_external_id": "c-MISSING", "user_external_id": "u-x", "role": "student"},
    )
    # enrollment -> user with no roster.user record (no email to resolve)
    _stage(
        db, conn, "roster.enrollment", "e-noid",
        {"class_external_id": "c-ok", "user_external_id": "u-ghost", "role": "student"},
    )
    # unknown role
    _stage(db, conn, "roster.user", "u-r", {"email": "r@sch2.example.edu"})
    _stage(
        db, conn, "roster.enrollment", "e-badrole",
        {"class_external_id": "c-ok", "user_external_id": "u-r", "role": "principal"},
    )
    # JIT disabled: unknown email queues as ambiguous
    _stage(db, conn, "roster.user", "u-new", {"email": "nojit@sch2.example.edu"})
    _stage(
        db, conn, "roster.enrollment", "e-nojit",
        {"class_external_id": "c-ok", "user_external_id": "u-new", "role": "student"},
    )
    await db.flush()
    report = await RosterProvisioningService(db).provision(
        org.id, conn.id, actor_id=owner.id, options={"jit_users": False}
    )
    assert report["conflicts"] == 4
    assert report["members_added"] == 0
    # ambiguity landed in the admin queue (resolvable, then next pass applies)
    q = (
        await db.execute(
            select(IdentityMatchQueue).where(IdentityMatchQueue.org_id == org.id)
        )
    ).scalars().all()
    assert {i.subject for i in q} >= {"u-new"}


@pytest.mark.asyncio
async def test_provision_role_conflict_reports_not_overwrites(db):
    org, owner = await _org(db)
    await _domain(db, org, "sch3.example.edu")
    conn = await _conn(db, org, owner)
    bob = await _user_member(db, org, "bob@sch3.example.edu")
    _stage(db, conn, "roster.class", "c-1", {"title": "C"})
    _stage(db, conn, "roster.user", "u-bob", {"email": "bob@sch3.example.edu"})
    _stage(
        db, conn, "roster.enrollment", "e-1",
        {"class_external_id": "c-1", "user_external_id": "u-bob", "role": "student"},
    )
    await db.flush()
    svc = RosterProvisioningService(db)
    await svc.provision(org.id, conn.id, actor_id=owner.id)
    # A human promotes bob to cohort instructor afterwards.
    cohort = (
        await db.execute(select(Cohort).where(Cohort.org_id == org.id))
    ).scalars().first()
    member = (
        await db.execute(
            select(CohortMember).where(
                CohortMember.cohort_id == cohort.id, CohortMember.user_id == bob.id
            )
        )
    ).scalar_one()
    member.role = CohortRole.INSTRUCTOR
    await db.flush()
    # SIS still says student: report a role_conflict, never demote.
    report = await svc.provision(org.id, conn.id, actor_id=owner.id)
    assert report["conflicts"] == 1
    await db.refresh(member)
    assert member.role == CohortRole.INSTRUCTOR


@pytest.mark.asyncio
async def test_unenroll_policy_removes_or_ignores(db):
    org, owner = await _org(db)
    await _domain(db, org, "sch4.example.edu")
    conn = await _conn(db, org, owner)
    await _user_member(db, org, "kid@sch4.example.edu")
    _stage(db, conn, "roster.class", "c-1", {"title": "C"})
    _stage(db, conn, "roster.user", "u-kid", {"email": "kid@sch4.example.edu"})
    _stage(
        db, conn, "roster.enrollment", "e-1",
        {"class_external_id": "c-1", "user_external_id": "u-kid", "role": "student"},
    )
    await db.flush()
    svc = RosterProvisioningService(db)
    await svc.provision(org.id, conn.id, actor_id=owner.id)
    # SIS tombstones the enrollment.
    rec = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id,
                StagedRecord.external_id == "e-1",
            )
        )
    ).scalar_one()
    rec.status = "tombstoned"
    await db.flush()
    # ignore policy: membership stays
    r1 = await svc.provision(org.id, conn.id, actor_id=owner.id, options={"on_unenroll": "ignore"})
    assert r1["members_removed"] == 0
    # remove policy: membership removed; submissions/portfolio untouched by design
    r2 = await svc.provision(org.id, conn.id, actor_id=owner.id)
    assert r2["members_removed"] == 1
    members = (
        await db.execute(
            select(CohortMember)
            .join(Cohort, Cohort.id == CohortMember.cohort_id)
            .where(Cohort.org_id == org.id)
        )
    ).scalars().all()
    assert members == []
    # cross-tenant uniform 404
    other, _ = await _org(db)
    with pytest.raises(AppError) as e:
        await svc.provision(other.id, conn.id, actor_id=owner.id)
    assert e.value.status_code == 404


# ── OneRoster connector vs faked SIS ──


class FakeSis:
    def __init__(self, pages):
        self.pages = pages  # list of lists of class dicts
        self.calls = []

    async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
        self.calls.append(url)
        parsed = urlsplit(url)
        if parsed.path.endswith("/token"):
            form = parse_qs((content or b"").decode())
            assert form["grant_type"] == ["client_credentials"]
            return httpx.Response(
                200, json={"access_token": "tok-1"}, request=httpx.Request(method, url)
            )
        qs = parse_qs(parsed.query)
        offset = int(qs.get("offset", ["0"])[0])
        limit = int(qs.get("limit", ["100"])[0])
        flat = [c for page in self.pages for c in page]
        items = flat[offset : offset + limit]
        assert headers["authorization"] == "Bearer tok-1"
        return httpx.Response(
            200, json={"classes": items}, request=httpx.Request(method, url)
        )


@pytest.mark.asyncio
async def test_oneroster_connector_pagination_and_mapping(db):
    from app.integrations.registry import ConnCtx, OneRosterConnector

    sis = FakeSis(
        [
            [
                {
                    "sourcedId": "cls-1",
                    "title": "Math",
                    "classCode": "M1",
                    "terms": [{"sourcedId": "t-1"}],
                    "school": {"sourcedId": "s-1"},
                    "grades": ["10"],
                }
            ]
            * 2  # 2 items -> with page_size 2 a second (empty) probe is avoided
        ]
    )

    async def loader():
        return {"client_id": "cid", "client_secret": "cs"}

    ctx = ConnCtx(
        connection_id="x",
        config={"token_url": "https://sis.example.com/token", "page_size": 2},
        base_url="https://sis.example.com/ims/oneroster/rostering/v1p2",
        _secret_loader=loader,
    )
    ctx.egress = sis
    connector = OneRosterConnector()
    batches = [b async for b in connector.read(ctx, "roster.class", {})]
    # 2 items == page_size -> engine reads one more (empty) page to finish
    all_records = [r for b in batches for r in b["records"]]
    assert len(all_records) == 2
    assert all_records[0]["external_id"] == "cls-1"
    assert all_records[0]["title"] == "Math"
    assert all_records[0]["term_external_id"] == "t-1"
    # final state resets to 0 for the next full read
    assert batches[-1]["state"] == {"endpoint_offset": 0}
    # unknown model refused
    with pytest.raises(AppError):
        async for _ in connector.read(ctx, "crm.deal", {}):
            pass


@pytest.mark.asyncio
async def test_oneroster_token_rejection(db):
    from app.integrations.registry import ConnCtx, OneRosterConnector

    class RefusingSis:
        async def request(self, method, url, **kw):
            return httpx.Response(401, json={}, request=httpx.Request(method, url))

    async def loader():
        return {"client_id": "cid", "client_secret": "WRONG"}

    ctx = ConnCtx(
        connection_id="x",
        config={"token_url": "https://sis.example.com/token"},
        base_url="https://sis.example.com/ims",
        _secret_loader=loader,
    )
    ctx.egress = RefusingSis()
    with pytest.raises(AppError) as e:
        async for _ in OneRosterConnector().read(ctx, "roster.class", {}):
            pass
    assert e.value.code == "CONNECTION_AUTH_REJECTED"
