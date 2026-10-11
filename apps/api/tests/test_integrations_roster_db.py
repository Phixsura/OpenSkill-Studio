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


# ── R38: roster probe killers ──


async def _run_for(db, conn, org):
    """Minimal profile+run so provision conflicts attach to record rows."""
    from app.integrations.models import SyncProfile, SyncRun

    prof = SyncProfile(
        org_id=org.id, connection_id=conn.id, name=f"rp-{uuid.uuid4().hex[:6]}",
        model="roster.class", direction="pull",
    )
    db.add(prof)
    await db.flush()
    run = SyncRun(profile_id=prof.id, status="succeeded", trigger="manual",
                  cursor_in={}, cursor_out={})
    db.add(run)
    await db.flush()
    return run


@pytest.mark.asyncio
async def test_conflict_classes_pinned_and_auto_create_off(db):
    """Kills: auto_create flag, missing_reference and role_conflict classes
    (the aggregate count alone passes even when a mutant reroutes the
    failure through a different arm)."""
    from app.integrations.models import SyncRecordResult

    org, owner = await _org(db)
    await _domain(db, org, "sch5.example.edu")
    conn = await _conn(db, org, owner)
    run = await _run_for(db, conn, org)
    _stage(db, conn, "roster.class", "c-off", {"title": "NoCreate"})
    _stage(db, conn, "roster.user", "u-5", {"email": "five@sch5.example.edu"})
    _stage(
        db, conn, "roster.enrollment", "e-dang",
        {"class_external_id": "c-NOPE", "user_external_id": "u-5", "role": "student"},
    )
    await db.flush()
    svc = RosterProvisioningService(db)
    report = await svc.provision(
        org.id, conn.id, actor_id=owner.id,
        options={"auto_create_cohorts": False, "jit_users": True},
    )
    assert report["cohorts_created"] == 0  # auto_create off honored
    rows = (
        await db.execute(
            select(SyncRecordResult).where(SyncRecordResult.run_id == run.id)
        )
    ).scalars().all()
    by_ext = {r.external_id: r for r in rows}
    assert by_ext["c-off"].detail == {"reason": "no_cohort_and_auto_create_off"}
    assert by_ext["e-dang"].conflict_class == "missing_reference"
    assert by_ext["e-dang"].detail == {"class_external_id": "c-NOPE"}

    # Second pass with auto_create ON: the cohort exists, so an unknown SIS
    # role is reported as role_conflict (not masked by missing_reference).
    _stage(
        db, conn, "roster.enrollment", "e-role",
        {"class_external_id": "c-off", "user_external_id": "u-5", "role": "principal"},
    )
    await db.flush()
    await svc.provision(org.id, conn.id, actor_id=owner.id, options={"jit_users": True})
    rows2 = (
        await db.execute(
            select(SyncRecordResult).where(
                SyncRecordResult.run_id == run.id,
                SyncRecordResult.external_id == "e-role",
            )
        )
    ).scalars().all()
    assert rows2 and rows2[0].conflict_class == "role_conflict"
    assert rows2[0].detail == {"role": "principal"}


@pytest.mark.asyncio
async def test_revoked_link_never_drives_unenroll(db):
    """A REVOKED identity link is not authoritative: a tombstoned enrollment
    for that subject must not remove the member."""
    from datetime import UTC, datetime

    from app.integrations.models import ExternalIdentityLink

    org, owner = await _org(db)
    await _domain(db, org, "sch6.example.edu")
    conn = await _conn(db, org, owner)
    await _user_member(db, org, "six@sch6.example.edu")
    _stage(db, conn, "roster.class", "c-6", {"title": "C6"})
    _stage(db, conn, "roster.user", "u-6", {"email": "six@sch6.example.edu"})
    _stage(
        db, conn, "roster.enrollment", "e-6",
        {"class_external_id": "c-6", "user_external_id": "u-6", "role": "student"},
    )
    await db.flush()
    svc = RosterProvisioningService(db)
    r = await svc.provision(org.id, conn.id, actor_id=owner.id)
    assert r["members_added"] == 1
    link = (
        await db.execute(
            select(ExternalIdentityLink).where(
                ExternalIdentityLink.connection_ref == conn.id,
                ExternalIdentityLink.subject == "u-6",
            )
        )
    ).scalar_one()
    link.revoked_at = datetime.now(UTC)
    rec = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id,
                StagedRecord.external_id == "e-6",
            )
        )
    ).scalar_one()
    rec.status = "tombstoned"
    await db.flush()
    r2 = await svc.provision(org.id, conn.id, actor_id=owner.id)
    assert r2["members_removed"] == 0


# ── R45: connector probe killers ──


def _ctx(egress, page_size=2):
    from app.integrations.registry import ConnCtx

    async def loader():
        return {"client_id": "cid", "client_secret": "cs"}

    ctx = ConnCtx(
        connection_id="x",
        config={"token_url": "https://sis.example.com/token", "page_size": page_size},
        base_url="https://sis.example.com/ims/oneroster/rostering/v1p2",
        _secret_loader=loader,
    )
    ctx.egress = egress
    return ctx


@pytest.mark.asyncio
async def test_oneroster_multi_page_and_overfull_page(db):
    """Kills: exact-full-page continuation (`<=` mutant stops early) and
    offset advancing by page_size instead of the REAL item count when a
    badly-behaved server over-returns."""
    from app.integrations.registry import OneRosterConnector

    def cls(i):
        return {"sourcedId": f"c-{i}", "title": f"T{i}"}

    # 4 items, page_size 2 -> two full pages + one empty probe; 4 records.
    sis = FakeSis([[cls(1), cls(2), cls(3), cls(4)]])
    connector = OneRosterConnector()
    batches = [b async for b in connector.read(_ctx(sis), "roster.class", {})]
    records = [r for b in batches for r in b["records"]]
    assert [r["external_id"] for r in records] == ["c-1", "c-2", "c-3", "c-4"]
    assert batches[-1]["state"] == {"endpoint_offset": 0}
    # Mid-run checkpoints carried the LIVE offset for crash resume.
    assert [b["state"]["endpoint_offset"] for b in batches[:-1]] == [2, 4]

    class OverfullSis(FakeSis):
        """Returns 3 items although limit=2 (server ignores the limit)."""

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            parsed = urlsplit(url)
            if parsed.path.endswith("/token"):
                return await super().request(
                    method, url, headers=headers, content=content, read_timeout=read_timeout
                )
            self.calls.append(url)
            offset = int(parse_qs(parsed.query).get("offset", ["0"])[0])
            flat = [c for page in self.pages for c in page]
            items = flat[offset : offset + 3]  # over-returns
            return httpx.Response(
                200, json={"classes": items}, request=httpx.Request(method, url)
            )

    over = OverfullSis([[cls(1), cls(2), cls(3)]])
    batches2 = [b async for b in connector.read(_ctx(over), "roster.class", {})]
    records2 = [r for b in batches2 for r in b["records"]]
    assert [r["external_id"] for r in records2] == ["c-1", "c-2", "c-3"]  # no dupes
    offsets = [parse_qs(urlsplit(u).query)["offset"][0] for u in over.calls if "offset" in u]
    assert offsets == ["0", "3"]  # offset advanced by REAL count


@pytest.mark.asyncio
async def test_oneroster_error_classification(db):
    """Kills: token 500 / missing access_token / data 401 vs 500 arms."""
    from app.integrations.registry import OneRosterConnector

    def scripted(token_status=200, token_json=None, data_status=200):
        class S:
            async def request(self, method, url, **kw):
                if urlsplit(url).path.endswith("/token"):
                    return httpx.Response(
                        token_status,
                        json=token_json if token_json is not None else {"access_token": "t"},
                        request=httpx.Request(method, url),
                    )
                return httpx.Response(
                    data_status, json={"classes": []}, request=httpx.Request(method, url)
                )
        return S()

    connector = OneRosterConnector()

    async def read_with(egress):
        return [b async for b in connector.read(_ctx(egress), "roster.class", {})]

    with pytest.raises(AppError) as e1:
        await read_with(scripted(token_status=500))
    assert e1.value.code == "CONNECTION_AUTH_REJECTED"
    with pytest.raises(AppError) as e2:
        await read_with(scripted(token_json={}))
    assert e2.value.code == "CONNECTION_AUTH_REJECTED"
    with pytest.raises(AppError) as e3:
        await read_with(scripted(data_status=401))
    assert e3.value.code == "CONNECTION_AUTH_REJECTED"
    with pytest.raises(AppError) as e4:
        await read_with(scripted(data_status=503))
    assert e4.value.code == "CONNECTION_PING_FAILED"


@pytest.mark.asyncio
async def test_whole_class_tombstone_still_removes_members(db):
    """R209: when the SIS removes an ENTIRE class, the backfill tombstones the
    class AND its enrollments. The unenroll pass used to look the cohort up
    only in the staged-ACTIVE class map — whole-class offboarding silently
    stopped removing members. The backlink fallback must remove them."""
    org, owner = await _org(db)
    await _domain(db, org, "sch9.example.edu")
    conn = await _conn(db, org, owner)
    await _user_member(db, org, "gone@sch9.example.edu")
    _stage(db, conn, "roster.class", "c-gone", {"title": "Closing"})
    _stage(db, conn, "roster.user", "u-gone", {"email": "gone@sch9.example.edu"})
    _stage(
        db, conn, "roster.enrollment", "e-gone",
        {"class_external_id": "c-gone", "user_external_id": "u-gone", "role": "student"},
    )
    await db.flush()
    svc = RosterProvisioningService(db)
    r0 = await svc.provision(org.id, conn.id, actor_id=owner.id)
    assert r0["members_added"] == 1

    # SIS deletes the whole class: class AND enrollment tombstone together.
    rows = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id,
                StagedRecord.external_id.in_(("c-gone", "e-gone")),
            )
        )
    ).scalars().all()
    assert len(rows) == 2
    for r in rows:
        r.status = "tombstoned"
    await db.flush()

    r1 = await svc.provision(org.id, conn.id, actor_id=owner.id)
    assert r1["members_removed"] == 1
    members = (
        await db.execute(
            select(CohortMember)
            .join(Cohort, Cohort.id == CohortMember.cohort_id)
            .where(Cohort.org_id == org.id)
        )
    ).scalars().all()
    assert members == []
