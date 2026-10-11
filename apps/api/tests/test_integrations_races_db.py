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
