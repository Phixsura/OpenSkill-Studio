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
