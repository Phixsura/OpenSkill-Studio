"""True-concurrency races over the fabric's atomic claims (R108).

Redelivery tests prove idempotency serially; these run TWO real sessions
through asyncio.gather so the UPDATE...WHERE claims are exercised under an
actual race, not a simulation."""

import asyncio
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
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
        email=f"race-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Race",
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
        name=f"Org {ULID()}", slug=f"o-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE, tenant_id=tenant.id, created_by=u.id,
    )
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=u.id, role=OrgRole.OWNER,
                     status=MemberStatus.ACTIVE))
    await db.flush()
    return org, u


@pytest.mark.asyncio
async def test_sync_run_claim_wins_exactly_once_under_race(db):
    """Two executors race the SAME queued run: the connector must read its
    batches exactly once (the queued->running claim arbitrates)."""
    from app.core.database import AsyncSessionLocal
    from app.integrations import registry
    from app.integrations.services.connections import ConnectionService
    from app.integrations.services.sync_engine import SyncProfileService, execute_run

    org, owner = await _org(db)
    csvc = ConnectionService(db)
    await csvc.sync_provider_catalog()
    await db.flush()
    conn = await csvc.create(
        org.id, provider_key="oneroster", name=f"rc-{uuid.uuid4().hex[:8]}",
        config={"token_url": "https://idp.example.com/token"},
        base_url="https://sis.example.com/ims/oneroster", created_by=owner.id,
    )
    conn.status = "active"

    class CountingConnector:
        key = "oneroster"
        capabilities = frozenset({"roster.read"})
        reads = 0

        async def ping(self, ctx):
            return None

        async def read(self, ctx, model, state):
            CountingConnector.reads += 1
            await asyncio.sleep(0.05)  # widen the race window
            yield {"records": [{"external_id": "race-1", "title": "T"}], "state": {}}

    registry.CONNECTORS["oneroster"] = CountingConnector()
    profile = await SyncProfileService(db).create(
        org.id, connection_id=conn.id, name=f"rp-{uuid.uuid4().hex[:6]}",
        model="roster.class", direction="pull", mapping_profile_id=None,
    )
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    run_id = run.id

    async def executor():
        async with AsyncSessionLocal() as own:
            await execute_run(own, run_id)

    await asyncio.gather(executor(), executor())
    from app.integrations.models import SyncRun

    row = await db.get(SyncRun, run_id)
    await db.refresh(row)
    assert row.status == "succeeded"
    assert CountingConnector.reads == 1  # exactly one executor ran the read
    assert row.stats.get("created") == 1


@pytest.mark.asyncio
async def test_import_commit_applies_exactly_once_under_race(db):
    """Two concurrent commits of the same previewed job: one wins, the
    loser gets IMPORT_NOT_COMMITTABLE, the row is applied once."""
    from sqlalchemy import func

    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.integrations.services.bulk_import import BulkImportService

    org, owner = await _org(db)
    email = f"rc-{uuid.uuid4().hex[:8]}@x.edu"
    data = f"email,display_name,role\n{email},Race,student\n".encode()
    job = await BulkImportService(db).create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="race", created_by=owner.id,
        idempotency_key=f"race-{uuid.uuid4().hex[:8]}",
    )
    await db.commit()
    job_id = job.id

    async def committer():
        async with AsyncSessionLocal() as own:
            try:
                await BulkImportService(own).commit(org.id, job_id, file_bytes=data)
                await own.commit()
                return "won"
            except AppError as exc:
                return exc.code

    results = await asyncio.gather(committer(), committer())
    assert sorted(results) == ["IMPORT_NOT_COMMITTABLE", "won"]
    n = (
        await db.execute(
            select(func.count()).select_from(User).where(func.lower(User.email) == email)
        )
    ).scalar_one()
    assert n == 1


@pytest.mark.asyncio
async def test_delivery_dispatch_race_is_at_least_once_consistent(db, monkeypatch):
    """Two dispatchers race ONE pending delivery. The mesh is at-least-once
    (receivers dedupe by webhook-id): duplicates are permitted, but the final
    state must be consistent — succeeded, every POST recorded as an attempt,
    identical bytes on the wire (the archive), and no retry scheduled."""
    import httpx

    from app.core.database import AsyncSessionLocal
    from app.integrations.facade import emit_event
    from app.integrations.models import DeliveryAttempt, EventDelivery
    from app.integrations.services import events as ev_mod
    from app.models.webhook import WebhookSubscription

    org, owner = await _org(db)
    db.add(WebhookSubscription(
        org_id=org.id, url="https://sink.example.com/h",
        events=["com.openskill.project.*"], secret="r" * 64, active=True,
    ))
    event = await emit_event(db, org.id, "project.approved", subject="race", data={})
    await db.commit()
    # Fan out once (serial) to mint the delivery row.
    async with AsyncSessionLocal() as s0:
        await ev_mod.handle_event_created(s0, {"event_id": event.id})
        await s0.commit()
    async with AsyncSessionLocal() as s0:
        from sqlalchemy import select as _sel

        delivery_id = (
            await s0.execute(
                _sel(EventDelivery.id).where(EventDelivery.event_id == event.id)
            )
        ).scalar_one()

    posts = []

    class SlowSink:
        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            posts.append(content)
            await asyncio.sleep(0.05)  # hold both dispatchers in flight
            return httpx.Response(200, request=httpx.Request(method, url))

    monkeypatch.setattr(ev_mod, "EgressClient", lambda: SlowSink())

    async def dispatcher():
        async with AsyncSessionLocal() as own:
            await ev_mod.handle_delivery_attempt(own, {"delivery_id": delivery_id})
            await own.commit()

    await asyncio.gather(dispatcher(), dispatcher())

    async with AsyncSessionLocal() as s1:
        from sqlalchemy import func as _f
        from sqlalchemy import select as _sel

        row = await s1.get(EventDelivery, delivery_id)
        attempts = (
            await s1.execute(
                _sel(_f.count()).select_from(DeliveryAttempt).where(
                    DeliveryAttempt.delivery_id == delivery_id
                )
            )
        ).scalar_one()
    assert row.status == "succeeded" and row.next_attempt_at is None
    assert 1 <= len(posts) <= 2 and attempts == len(posts)
    assert len({bytes(p) for p in posts}) == 1  # byte-identical wire bodies


@pytest.mark.asyncio
async def test_sso_first_login_race_single_link(db):
    """Two concurrent FIRST logins for the same subject: the partial-unique
    index arbitrates; both resolve to the SAME user, exactly one active
    link row exists."""
    from datetime import UTC, datetime

    from app.core.database import AsyncSessionLocal
    from app.integrations.models import ExternalIdentityLink, OrgDomain
    from app.integrations.services.identity import (
        IdentityService,
        VerifiedExternalIdentity,
    )

    org, owner = await _org(db)
    domain = f"race-{uuid.uuid4().hex[:6]}.io"
    db.add(OrgDomain(org_id=org.id, domain=domain, status="verified",
                     verification_token="t", verified_at=datetime.now(UTC)))
    member = User(
        email=f"kid@{domain}", password_hash=hash_password("Test123!"),
        display_name="Kid", role=UserRole.STUDENT, status=UserStatus.ACTIVE,
    )
    db.add(member)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=member.id, role=OrgRole.STUDENT,
                     status=MemberStatus.ACTIVE))
    await db.commit()
    subject = f"race-sub-{uuid.uuid4().hex[:6]}"
    conn_ref = f"01RACE{uuid.uuid4().hex[:20].upper()}"

    async def login():
        async with AsyncSessionLocal() as own:
            ident = VerifiedExternalIdentity(
                org_id=org.id, source="sso", connection_ref=conn_ref,
                subject=subject, email=f"kid@{domain}", email_verified=True,
            )
            res = await IdentityService(own).resolve(ident)
            await own.commit()
            return res.user.id

    u1, u2 = await asyncio.gather(login(), login())
    assert u1 == u2 == member.id
    links = (
        await db.execute(
            select(ExternalIdentityLink).where(
                ExternalIdentityLink.connection_ref == conn_ref,
                ExternalIdentityLink.subject == subject,
                ExternalIdentityLink.revoked_at.is_(None),
            )
        )
    ).scalars().all()
    assert len(links) == 1


@pytest.mark.asyncio
async def test_tool_key_concurrent_first_use_single_key(db):
    """R111: two concurrent ensure_tool_key calls — the singleton index
    arbitrates, the loser gets the winner's key, neither session poisons."""
    from app.core.database import AsyncSessionLocal
    from app.integrations.services.lti_ags import ensure_tool_key

    async def miner():
        async with AsyncSessionLocal() as own:
            key = await ensure_tool_key(own)
            await own.commit()
            return key.kid

    kids = await asyncio.gather(miner(), miner())
    assert kids[0] == kids[1]


@pytest.mark.asyncio
async def test_webhook_cap_holds_under_concurrent_creates(db):
    """R113: the per-org webhook cap uses a FOR UPDATE org lock — two
    concurrent creates at cap-1 must yield exactly one success."""
    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.webhook import WebhookSubscription
    from app.services.webhook import MAX_WEBHOOKS_PER_ORG, WebhookService

    org, owner = await _org(db)
    for i in range(MAX_WEBHOOKS_PER_ORG - 1):
        db.add(WebhookSubscription(
            org_id=org.id, url=f"https://sink{i}.example.com/h",
            events=["project.approved"], secret="c" * 64, active=True,
        ))
    await db.commit()

    async def creator(n):
        async with AsyncSessionLocal() as own:
            try:
                await WebhookService(own).create(
                    org.id, f"https://racer{n}.example.com/h", ["credential.issued"],
                    actor_user_id=owner.id,
                )
                await own.commit()
                return "won"
            except AppError as exc:
                return exc.code

    results = sorted(await asyncio.gather(creator(1), creator(2)))
    assert results == ["WEBHOOK_LIMIT_REACHED", "won"]
    from sqlalchemy import func as _f

    n = (
        await db.execute(
            select(_f.count()).select_from(WebhookSubscription).where(
                WebhookSubscription.org_id == org.id
            )
        )
    ).scalar_one()
    assert n == MAX_WEBHOOKS_PER_ORG


@pytest.mark.asyncio
async def test_domain_verify_exclusivity_under_race(db, monkeypatch):
    """R113: two orgs' admins click Verify on the SAME domain at once — the
    partial-unique index lets exactly one succeed, the loser gets a clean
    409 (not a poisoned session)."""
    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.integrations.models import OrgDomain
    from app.integrations.services import domains as dom_mod
    from app.integrations.services.domains import OrgDomainService

    org1, _ = await _org(db)
    org2, _ = await _org(db)
    domain = f"race-dom-{uuid.uuid4().hex[:6]}.io"
    ids = {}
    for org in (org1, org2):
        d = OrgDomain(org_id=org.id, domain=domain, status="pending",
                      verification_token="t")
        db.add(d)
        await db.flush()
        ids[org.id] = d.id
    await db.commit()

    class YesVerifier:
        async def verify(self, host, token):
            await asyncio.sleep(0.03)
            return True

    monkeypatch.setattr(dom_mod, "get_verifier", lambda: YesVerifier())

    async def verifier(org_id):
        async with AsyncSessionLocal() as own:
            try:
                await OrgDomainService(own).verify(org_id, ids[org_id])
                await own.commit()
                return "won"
            except AppError as exc:
                return exc.code

    results = sorted(await asyncio.gather(verifier(org1.id), verifier(org2.id)))
    assert results == ["DOMAIN_ALREADY_VERIFIED", "won"]
    verified = (
        await db.execute(
            select(OrgDomain.status).where(OrgDomain.domain == domain)
        )
    ).scalars().all()
    assert verified.count("verified") == 1
    # Clean up the COMMITTED rows so the global sweep_pending (no org filter)
    # in sibling tests never trips over a leftover same-domain pending pair.
    async with AsyncSessionLocal() as cleanup:
        from sqlalchemy import delete as _del
        await cleanup.execute(_del(OrgDomain).where(OrgDomain.domain == domain))
        await cleanup.commit()



@pytest.mark.asyncio
async def test_roster_import_race_single_membership(db):
    """R136: TWO different roster jobs for the same (user, cohort) pair
    committed concurrently — the unique index decides; the loser's row
    fails cleanly inside its savepoint (partial job, apply_failed or skip),
    neither session 500s, and exactly ONE membership lands."""
    from sqlalchemy import func

    from app.core.database import AsyncSessionLocal
    from app.integrations.services.bulk_import import BulkImportService
    from app.models.cohort import Cohort, CohortMember

    org, owner = await _org(db)
    cohort = Cohort(
        org_id=org.id, name="Race Cohort", slug=f"race-{uuid.uuid4().hex[:8]}",
        created_by=owner.id,
    )
    db.add(cohort)
    await db.flush()
    email = f"rr-{uuid.uuid4().hex[:8]}@x.edu"
    useed = f"email\n{email}\n".encode()
    svc = BulkImportService(db)
    ujob = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=useed,
        file_key="u", created_by=owner.id, idempotency_key=f"rru-{uuid.uuid4().hex[:8]}",
    )
    await svc.commit(org.id, ujob.id, file_bytes=useed)

    data = f"email,cohort_slug\n{email},{cohort.slug}\n".encode()
    job_ids = []
    for i in range(2):
        j = await svc.create_job(
            org.id, kind="roster", mode="partial", file_bytes=data,
            file_key=f"r{i}", created_by=owner.id,
            idempotency_key=f"rrj{i}-{uuid.uuid4().hex[:8]}",
        )
        job_ids.append(j.id)
    await db.commit()
    cohort_id, org_id = cohort.id, org.id

    async def committer(job_id):
        async with AsyncSessionLocal() as own:
            job = await BulkImportService(own).commit(org_id, job_id, file_bytes=data)
            status, stats = job.status, dict(job.stats or {})
            await own.commit()
            return status, stats

    results = await asyncio.gather(
        committer(job_ids[0]), committer(job_ids[1]), return_exceptions=True
    )
    for r in results:
        assert not isinstance(r, BaseException), f"a session blew up: {r!r}"
        status, stats = r
        assert status in ("succeeded", "partial"), (status, stats)
    created_total = sum(r[1].get("created", 0) for r in results)
    n = (
        await db.execute(
            select(func.count()).select_from(CohortMember).where(
                CohortMember.cohort_id == cohort_id
            )
        )
    ).scalar_one()
    assert n == 1, f"expected exactly one membership, got {n} ({results})"
    assert created_total == 1, results


@pytest.mark.asyncio
async def test_concurrent_jit_provision_single_user(db):
    """R166: two concurrent FIRST-TIME SSO logins for the same brand-new
    verified email must JIT exactly one User (and one membership), with
    neither session poisoned by a unique-violation 500 — the add-before-
    savepoint class the marathon-2 race tests found elsewhere."""
    from datetime import UTC, datetime

    from sqlalchemy import func

    from app.core.database import AsyncSessionLocal
    from app.integrations.models import OrgDomain
    from app.integrations.services.identity import (
        IdentityService,
        VerifiedExternalIdentity,
    )
    from app.models.organization import OrgMember as OrgMemberModel
    from app.models.user import User as _User

    org, owner = await _org(db)
    domain = f"jit-{uuid.uuid4().hex[:6]}.edu"
    db.add(OrgDomain(org_id=org.id, domain=domain, status="verified",
                     verification_token="t", verified_at=datetime.now(UTC)))
    await db.commit()
    email = f"newbie-{uuid.uuid4().hex[:8]}@{domain}"
    conn_ref = f"01JIT{uuid.uuid4().hex[:21].upper()}"

    async def login(sub_suffix):
        async with AsyncSessionLocal() as own:
            ident = VerifiedExternalIdentity(
                org_id=org.id, source="sso", connection_ref=conn_ref,
                subject=f"jit-sub-{sub_suffix}", email=email, email_verified=True,
            )
            res = await IdentityService(own).resolve(ident, allow_jit=True, jit_role="student")
            await own.commit()
            return res.user.id

    # DIFFERENT subjects, SAME new email: both take the JIT branch and race
    # to INSERT the same User.email.
    results = await asyncio.gather(login("a"), login("b"), return_exceptions=True)
    for r in results:
        assert not isinstance(r, BaseException), f"a login session blew up: {r!r}"
    assert results[0] == results[1], "both logins must resolve to the same user"

    users = (
        await db.execute(select(_User).where(func.lower(_User.email) == email))
    ).scalars().all()
    assert len(users) == 1, f"JIT created {len(users)} users for one email"
    members = (
        await db.execute(
            select(OrgMemberModel).where(OrgMemberModel.org_id == org.id, OrgMemberModel.user_id == users[0].id)
        )
    ).scalars().all()
    assert len(members) == 1


@pytest.mark.asyncio
async def test_concurrent_membership_jit_single_member(db):
    """R166: two concurrent logins of the SAME existing platform user into
    the SAME org (membership-only JIT) must create exactly one OrgMember,
    neither session poisoned by the uq_org_member violation."""
    from datetime import UTC, datetime

    from app.core.database import AsyncSessionLocal
    from app.integrations.models import OrgDomain
    from app.integrations.services.identity import (
        IdentityService,
        VerifiedExternalIdentity,
    )
    from app.models.organization import OrgMember as OrgMemberModel

    org, owner = await _org(db)
    domain = f"mjit-{uuid.uuid4().hex[:6]}.edu"
    db.add(OrgDomain(org_id=org.id, domain=domain, status="verified",
                     verification_token="t", verified_at=datetime.now(UTC)))
    email = f"exist-{uuid.uuid4().hex[:8]}@{domain}"
    # An ACTIVE platform user that is NOT yet a member of this org.
    platform_user = User(
        email=email, password_hash=hash_password("Test123!"),
        display_name="Exist", role=UserRole.STUDENT, status=UserStatus.ACTIVE,
    )
    db.add(platform_user)
    await db.commit()
    conn_ref = f"01MJIT{uuid.uuid4().hex[:20].upper()}"

    async def login(sub_suffix):
        async with AsyncSessionLocal() as own:
            ident = VerifiedExternalIdentity(
                org_id=org.id, source="sso", connection_ref=conn_ref,
                subject=f"mjit-sub-{sub_suffix}", email=email, email_verified=True,
            )
            res = await IdentityService(own).resolve(ident, allow_jit=True, jit_role="student")
            await own.commit()
            return res.user.id

    results = await asyncio.gather(login("a"), login("b"), return_exceptions=True)
    for r in results:
        assert not isinstance(r, BaseException), f"a login session blew up: {r!r}"
    assert results[0] == results[1] == platform_user.id

    members = (
        await db.execute(
            select(OrgMemberModel).where(
                OrgMemberModel.org_id == org.id,
                OrgMemberModel.user_id == platform_user.id,
            )
        )
    ).scalars().all()
    assert len(members) == 1
