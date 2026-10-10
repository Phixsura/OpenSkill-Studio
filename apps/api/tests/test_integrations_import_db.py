"""P8 tests — bulk import pipeline (parse, dry-run, staleness, atomic vs
partial commit, idempotent re-upload, CSV-injection-safe error report)."""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.services.bulk_import import (
    BulkImportService,
    fingerprint,
    parse_users_csv,
)
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
        email=f"im-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Im",
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


def _csv(rows, header="email,display_name,role"):
    return (header + "\r\n" + "\r\n".join(rows)).encode()


# ── parser ──


def test_parse_matrix():
    # BOM + CRLF + extra column + case-insensitive headers all tolerated
    data = "﻿Email,Display_Name,ROLE,extra\r\na@x.edu,Alice,student,zz\r\n".encode()
    rows, errors = parse_users_csv(data)
    assert errors == [] and rows[0]["email"] == "a@x.edu" and rows[0]["row_number"] == 2
    # missing required column fails the FILE before any row
    rows2, errors2 = parse_users_csv(b"name,role\r\nAlice,student\r\n")
    assert rows2 == [] and errors2[0]["code"] == "missing_column"
    # per-row problems collected, not first-error aborted; dup detection
    data3 = _csv(
        [
            "good@x.edu,G,student",
            "bad-email,B,student",
            "role@x.edu,R,principal",
            "good@x.edu,G2,student",  # dup of row 2
        ]
    )
    rows3, errors3 = parse_users_csv(data3)
    assert len(rows3) == 1  # only good@x.edu survives
    codes = {e["code"] for e in errors3}
    assert codes == {"invalid_email", "invalid_role", "duplicate_in_file"}
    # 1-indexed + header: duplicate message points at the FIRST occurrence row
    dup = next(e for e in errors3 if e["code"] == "duplicate_in_file")
    assert dup["row_number"] == 5 and "row 2" in dup["message"]
    # non-UTF8 file
    rows4, errors4 = parse_users_csv(b"\xff\xfe\x00bad")
    assert errors4[0]["code"] == "encoding"


# ── job lifecycle ──


@pytest.mark.asyncio
async def test_preview_commit_and_idempotent_reupload(db):
    org, owner = await _org(db)
    existing = User(
        email=f"have-{uuid.uuid4().hex[:6]}@x.edu",
        password_hash=hash_password("Test123!"),
        display_name="Old Name",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(existing)
    await db.flush()
    fresh = f"new-{uuid.uuid4().hex[:6]}@x.edu"
    data = _csv(
        [
            f"{fresh},Newbie,student",
            f"{existing.email},New Name,instructor",
        ]
    )
    svc = BulkImportService(db)
    job = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="k1", created_by=owner.id, idempotency_key="idem-1",
    )
    assert job.status == "previewed"
    assert job.dry_stats == {"valid": 2, "errors": 0, "creates": 1, "updates": 1, "skips": 0}
    # idempotent re-upload returns the SAME job
    again = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="k2", created_by=owner.id, idempotency_key="idem-1",
    )
    assert again.id == job.id

    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.status == "succeeded"
    assert committed.stats["created"] == 1 and committed.stats["updated"] == 1
    new_user = (
        await db.execute(select(User).where(func.lower(User.email) == fresh))
    ).scalar_one()
    assert new_user.email_verified is False  # imported, not IdP-verified
    await db.refresh(existing)
    assert existing.display_name == "New Name"
    member = (
        await db.execute(
            select(OrgMember).where(
                OrgMember.org_id == org.id, OrgMember.user_id == existing.id
            )
        )
    ).scalar_one()
    assert member.role == OrgRole.INSTRUCTOR  # initial role from the file

    # Re-commit refused; second full import of the same file = all skips.
    with pytest.raises(AppError) as e:
        await svc.commit(org.id, job.id, file_bytes=data)
    assert e.value.code == "IMPORT_NOT_COMMITTABLE"
    job2 = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="k3", created_by=owner.id,
    )
    committed2 = await svc.commit(org.id, job2.id, file_bytes=data)
    assert committed2.stats["created"] == 0
    # existing member roles are NEVER changed by re-imports
    await db.refresh(member)
    assert member.role == OrgRole.INSTRUCTOR


@pytest.mark.asyncio
async def test_stale_preview_refused(db):
    org, owner = await _org(db)
    data = _csv([f"a-{uuid.uuid4().hex[:6]}@x.edu,A,student"])
    svc = BulkImportService(db)
    job = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="k", created_by=owner.id,
    )
    drifted = data + b"\r\nnew@x.edu,N,student"
    with pytest.raises(AppError) as e:
        await svc.commit(org.id, job.id, file_bytes=drifted)
    assert e.value.code == "IMPORT_DRY_RUN_STALE"
    assert fingerprint(data, 1) != fingerprint(drifted, 1)


@pytest.mark.asyncio
async def test_atomic_mode_rejects_whole_file(db):
    org, owner = await _org(db)
    good = f"ok-{uuid.uuid4().hex[:6]}@x.edu"
    data = _csv([f"{good},G,student", "broken-email,B,student"])
    svc = BulkImportService(db)
    job = await svc.create_job(
        org.id, kind="users", mode="atomic", file_bytes=data,
        file_key="k", created_by=owner.id,
    )
    assert job.dry_stats["errors"] == 1
    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.status == "failed"
    assert committed.stats["reason"] == "atomic_reject"
    # NOTHING applied — the good row did not land.
    assert (
        await db.execute(select(User).where(func.lower(User.email) == good))
    ).scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_partial_mode_applies_valid_rows_and_error_report(db):
    org, owner = await _org(db)
    good = f"ok-{uuid.uuid4().hex[:6]}@x.edu"
    data = _csv(
        [
            f"{good},G,student",
            "=HYPERLINK(evil)@bad,Formula,student",  # bad email AND formula cell
        ]
    )
    svc = BulkImportService(db)
    job = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="k", created_by=owner.id,
    )
    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.status == "partial"
    assert committed.stats["applied"] == 1
    assert (
        await db.execute(select(User).where(func.lower(User.email) == good))
    ).scalar_one_or_none() is not None
    report = await svc.errors_csv(org.id, job.id)
    assert "invalid_email" in report
    # CSV-injection sanitization: formula-leading cells are quote-prefixed.
    assert "=HYPERLINK" not in report.replace("'=HYPERLINK", "")


@pytest.mark.asyncio
async def test_import_cross_org_404_and_caps(db):
    org, owner = await _org(db)
    svc = BulkImportService(db)
    with pytest.raises(AppError) as e:
        await svc.create_job(
            org.id, kind="users", mode="partial",
            file_bytes=b"x" * (52_428_800 + 1), file_key="k", created_by=owner.id,
        )
    assert e.value.code == "IMPORT_TOO_LARGE"
    with pytest.raises(AppError):
        await svc.create_job(
            org.id, kind="nope", mode="partial", file_bytes=b"a", file_key="k",
            created_by=owner.id,
        )
    data = _csv([f"a-{uuid.uuid4().hex[:6]}@x.edu,A,student"])
    job = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data, file_key="k",
        created_by=owner.id,
    )
    other, _ = await _org(db)
    for call in (
        lambda: svc.get(other.id, job.id),
        lambda: svc.commit(other.id, job.id, file_bytes=data),
        lambda: svc.errors_csv(other.id, job.id),
    ):
        with pytest.raises(AppError) as e2:
            await call()
        assert e2.value.status_code == 404


# ── R7 adversarial-review regression pins ──


@pytest.mark.asyncio
async def test_concurrent_commit_single_winner(db):
    org, owner = await _org(db)
    data = _csv([f"cc-{uuid.uuid4().hex[:6]}@x.edu,A,student"])
    svc = BulkImportService(db)
    job = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="k", created_by=owner.id,
    )
    # First commit wins; a racer that lost the claim gets 409 even with the
    # right fingerprint.
    await svc.commit(org.id, job.id, file_bytes=data)
    with pytest.raises(AppError) as e:
        await svc.commit(org.id, job.id, file_bytes=data)
    assert e.value.code == "IMPORT_NOT_COMMITTABLE"
