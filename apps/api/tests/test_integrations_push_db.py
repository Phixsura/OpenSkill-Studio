"""P10 tests — consent-gated outbound ATS push (talent.application)."""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.models import StagedRecord
from app.integrations.services.sync_engine import SyncProfileService, execute_run
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus
from app.talent.models.application import Application
from app.talent.models.consent_log import ConsentLog
from app.talent.models.employer import Opportunity


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, email=None):
    u = User(
        email=email or f"pu-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Pu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db):
    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    u = await _user(db)
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


class FakeAtsConnector:
    key = "generic_ats"
    capabilities = frozenset({"talent.write"})

    def __init__(self, fail_ids=()):
        self.fail_ids = set(fail_ids)
        self.batches: list[list[dict]] = []

    async def ping(self, ctx):
        return None

    async def write(self, ctx, model, records):
        self.batches.append(records)
        return [
            {
                "external_id": r["external_id"],
                "ok": r["external_id"] not in self.fail_ids,
                "error": "boom" if r["external_id"] in self.fail_ids else None,
            }
            for r in records
        ]


async def _setup(db, org, owner, connector):
    from app.integrations import registry
    from app.integrations.services.connections import ConnectionService

    csvc = ConnectionService(db)
    await csvc.sync_provider_catalog()
    await db.flush()
    conn = await csvc.create(
        org.id,
        provider_key="generic_ats",
        name=f"ats-{uuid.uuid4().hex[:8]}",
        config={},
        base_url="https://ats.example.com/api",
        created_by=owner.id,
    )
    conn.status = "active"
    registry.CONNECTORS["generic_ats"] = connector
    profile = await SyncProfileService(db).create(
        org.id,
        connection_id=conn.id,
        name=f"push-{uuid.uuid4().hex[:6]}",
        model="talent.application",
        direction="push",
        mapping_profile_id=None,
    )
    await db.commit()
    return conn, profile


async def _application(db, org, status="submitted", consent=None):
    candidate = await _user(db)
    opp = Opportunity(
        employer_org_id=org.id,
        title=f"Role {uuid.uuid4().hex[:5]}",
        opportunity_type="internship",
        status="open",
    )
    db.add(opp)
    await db.flush()
    app_row = Application(opportunity_id=opp.id, user_id=candidate.id, status=status)
    db.add(app_row)
    if consent is not None:
        db.add(ConsentLog(user_id=candidate.id, consent_type="ats_share", action=consent))
    await db.flush()
    return app_row, candidate


@pytest.mark.asyncio
async def test_push_consent_gate_and_change_detection(db):
    org, owner = await _org(db)
    fake = FakeAtsConnector()
    conn, profile = await _setup(db, org, owner, fake)
    app_ok, cand_ok = await _application(db, org, consent="granted")
    app_no, cand_no = await _application(db, org, consent=None)
    app_revoked, _ = await _application(db, org, consent="revoked")
    await db.commit()

    svc = SyncProfileService(db)
    run = await svc.trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    await db.refresh(run)
    assert run.status == "partial"  # 2 consent conflicts
    assert run.stats["pushed"] == 1 and run.stats["conflicts"] == 2
    sent = [r["external_id"] for b in fake.batches for r in b]
    assert sent == [app_ok.id]
    # Privacy shape: ids + pipeline position only.
    pushed = fake.batches[0][0]
    assert set(pushed) == {
        "external_id",
        "application_id",
        "opportunity_id",
        "opportunity_title",
        "candidate_user_id",
        "status",
    }
    conflicts = await svc.run_records(org.id, run.id, outcome="conflict")
    assert {c.conflict_class for c in conflicts} == {"consent_missing"}
    # last_outbound recorded for echo suppression
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id,
                StagedRecord.external_id == app_ok.id,
            )
        )
    ).scalar_one()
    assert staged.last_outbound["fields_hash"]

    # Unchanged second run pushes nothing.
    fake.batches.clear()
    run2 = await svc.trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run2.id)
    await db.refresh(run2)
    assert run2.stats["pushed"] == 0 and run2.stats["unchanged"] == 1
    assert fake.batches == []

    # Status change re-pushes; revoking consent stops future pushes.
    app_ok.status = "interview"
    db.add(ConsentLog(user_id=cand_ok.id, consent_type="ats_share", action="revoked"))
    await db.commit()
    run3 = await svc.trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run3.id)
    await db.refresh(run3)
    assert run3.stats["pushed"] == 0
    assert run3.stats["conflicts"] == 3  # all three now unconsented


@pytest.mark.asyncio
async def test_push_write_failures_recorded(db):
    org, owner = await _org(db)
    app_row, cand = await _application(db, org, consent="granted")
    fake = FakeAtsConnector(fail_ids={app_row.id})
    conn, profile = await _setup(db, org, owner, fake)
    await db.commit()
    svc = SyncProfileService(db)
    run = await svc.trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    await db.refresh(run)
    assert run.status == "partial" and run.stats["errors"] == 1
    errors = await svc.run_records(org.id, run.id, outcome="error")
    assert errors[0].detail["error"] == "boom"
    # Failed write leaves NO last_outbound (it will retry next run).
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id,
                StagedRecord.external_id == app_row.id,
            )
        )
    ).scalar_one()
    assert staged.last_outbound == {}


@pytest.mark.asyncio
async def test_push_requires_write_capability(db):
    org, owner = await _org(db)
    from app.integrations.services.connections import ConnectionService

    csvc = ConnectionService(db)
    await csvc.sync_provider_catalog()
    conn = await csvc.create(
        org.id,
        provider_key="oneroster",  # read-only provider
        name=f"c-{uuid.uuid4().hex[:8]}",
        config={"token_url": "https://sis.example.com/token"},
        base_url="https://sis.example.com/x",
        created_by=owner.id,
    )
    with pytest.raises(AppError) as e:
        await SyncProfileService(db).create(
            org.id,
            connection_id=conn.id,
            name="p",
            model="talent.application",
            direction="push",
            mapping_profile_id=None,
        )
    assert e.value.code == "CAPABILITY_MISSING"
