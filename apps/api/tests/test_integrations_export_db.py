"""P9 tests — governed warehouse export: allowlist discipline (R82),
anonymization, incremental cursors, manifest freshness."""

import hashlib
import json
import uuid

import pytest
import pytest_asyncio
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.facade import emit_event
from app.integrations.services.warehouse import (
    DATASETS,
    WarehouseExportService,
)
from app.models.cohort import CohortRole
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
        email=f"ex-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Ex",
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


class MemWriter:
    def __init__(self):
        self.files: dict[str, bytes] = {}

    async def write(self, key: str, content: bytes) -> None:
        self.files[key] = content


def test_default_allowlists_cover_the_universe():
    """R82 total-coverage: every default allowlist ⊆ the dataset universe,
    and every universe field is either exported-by-default or deliberately
    absent (documented in the DATASETS spec)."""
    for name, spec in DATASETS.items():
        assert set(spec["default_allowlist"]) <= spec["fields"], name


@pytest.mark.asyncio
async def test_stream_config_rules(db):
    org, _ = await _org(db)
    svc = WarehouseExportService(db)
    with pytest.raises(AppError) as e:
        await svc.create_stream(org.id, name="x", dataset="passwords")
    assert e.value.code == "EXPORT_DATASET_UNKNOWN"
    # a field outside the universe is refused AT CONFIG TIME
    with pytest.raises(AppError) as e2:
        await svc.create_stream(
            org.id, name="x", dataset="events", field_allowlist=["id", "data"]
        )
    assert e2.value.code == "EXPORT_FIELD_NOT_ALLOWED"
    with pytest.raises(AppError) as e3:
        await svc.create_stream(
            org.id, name="x", dataset="enrollments", anonymize={"user_id": "rot13"}
        )
    assert e3.value.code == "EXPORT_CONFIG_INVALID"
    s = await svc.create_stream(org.id, name=f"s-{ULID()}", dataset="enrollments")
    assert s.anonymize == {"user_id": "hash"}  # safe default
    # cross-tenant uniform 404
    other, _ = await _org(db)
    with pytest.raises(AppError) as e4:
        await svc.get_stream(other.id, s.id)
    assert e4.value.status_code == 404


@pytest.mark.asyncio
async def test_export_events_incremental_and_tenant_scoped(db):
    org, owner = await _org(db)
    other_org, _ = await _org(db)
    for i in range(3):
        await emit_event(db, org.id, "project.approved", subject=f"p{i}", data={})
    await emit_event(db, other_org.id, "project.approved", subject="FOREIGN", data={})
    await db.flush()

    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    stream = await svc.create_stream(org.id, name=f"ev-{ULID()}", dataset="events")
    run = await svc.run_export(org.id, stream.id)
    assert run.status == "succeeded" and run.row_count == 3
    manifest = json.loads(writer.files[run.manifest_key])
    assert manifest["row_count"] == 3 and manifest["schema_version"] == 1
    assert manifest["generated_at"]  # freshness first-class
    part = writer.files[run.parts[0]].decode().strip().split("\n")
    rows = [json.loads(line) for line in part]
    # Tenant boundary enforced in the query: the foreign org's event absent.
    assert all(r["subject"] != "FOREIGN" for r in rows)
    # Allowlist-built rows: no `data`, no `org_id`, nothing unlisted.
    assert set(rows[0]) == {"id", "type", "subject", "time"}

    # Incremental: a second run exports only NEW events.
    await emit_event(db, org.id, "project.approved", subject="p-new", data={})
    await db.flush()
    run2 = await svc.run_export(org.id, stream.id)
    assert run2.row_count == 1
    rows2 = [
        json.loads(line)
        for line in writer.files[run2.parts[0]].decode().strip().split("\n")
    ]
    assert rows2[0]["subject"] == "p-new"
    # Empty incremental run: zero rows, no parts, cursor unchanged.
    run3 = await svc.run_export(org.id, stream.id)
    assert run3.row_count == 0 and run3.parts == []


@pytest.mark.asyncio
async def test_export_enrollments_hash_and_drop(db):
    from app.services.cohort import CohortService

    org, owner = await _org(db)
    csvc = CohortService(db)
    cohort = await csvc.create_cohort(
        org_id=org.id, name=f"C {ULID()}", description=None, created_by=owner.id
    )
    learner = User(
        email=f"l-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="L",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(learner)
    await db.flush()
    db.add(
        OrgMember(
            org_id=org.id, user_id=learner.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE
        )
    )
    await db.flush()
    await csvc.add_member(cohort.id, learner.id, CohortRole.LEARNER, org.id)

    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    # default: user_id hashed
    s1 = await svc.create_stream(org.id, name=f"en-{ULID()}", dataset="enrollments")
    r1 = await svc.run_export(org.id, s1.id)
    rows = [
        json.loads(line)
        for line in writer.files[r1.parts[0]].decode().strip().split("\n")
    ]
    assert rows[0]["user_id"] != learner.id  # hashed
    assert len(rows[0]["user_id"]) == 32
    assert rows[0]["cohort_name"].startswith("C ")
    # drop mode: the field is structurally absent
    s2 = await svc.create_stream(
        org.id,
        name=f"en2-{ULID()}",
        dataset="enrollments",
        anonymize={"user_id": "drop"},
    )
    r2 = await svc.run_export(org.id, s2.id)
    rows2 = [
        json.loads(line)
        for line in writer.files[r2.parts[0]].decode().strip().split("\n")
    ]
    assert "user_id" not in rows2[0]
    # per-org salt: same user exported by another org hashes DIFFERENTLY
    salted = hashlib.sha256(f"x:{learner.id}".encode()).hexdigest()[:32]
    assert rows[0]["user_id"] != salted  # not an unsalted/global hash
