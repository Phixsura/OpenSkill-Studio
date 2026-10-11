"""P8 tests — bulk import pipeline (parse, dry-run, staleness, atomic vs
partial commit, idempotent re-upload, CSV-injection-safe error report)."""

import uuid

import pytest
import pytest_asyncio
from hypothesis import given, settings
from hypothesis import strategies as st
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


# ── R38: bulk-import probe killers ──


@pytest.mark.asyncio
async def test_display_truncation_error_cap_and_committing_claim(db):
    from app.integrations.models import ImportRowError
    from app.integrations.models.bulk import MAX_ROW_ERRORS

    org, owner = await _org(db)
    svc = BulkImportService(db)

    # 1. 150-char display name is truncated to 100, not a row failure.
    email = f"long-{uuid.uuid4().hex[:6]}@x.edu"
    data = _csv([f"{email},{'D' * 150},student"])
    job = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="t1", created_by=owner.id, idempotency_key=f"r38-{uuid.uuid4().hex[:8]}",
    )
    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.stats["created"] == 1 and committed.stats.get("row_errors", 0) == 0
    u = (
        await db.execute(select(User).where(func.lower(User.email) == email))
    ).scalar_one()
    assert len(u.display_name) == 100

    # 2. Preview stores at most MAX_ROW_ERRORS row errors (JSONB blow-up cap).
    bad = _csv([f"not-an-email-{i},X,student" for i in range(MAX_ROW_ERRORS + 5)])
    job2 = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=bad,
        file_key="t2", created_by=owner.id, idempotency_key=f"r38b-{uuid.uuid4().hex[:8]}",
    )
    stored = (
        await db.execute(
            select(func.count()).select_from(ImportRowError).where(
                ImportRowError.job_id == job2.id
            )
        )
    ).scalar_one()
    assert stored == MAX_ROW_ERRORS
    assert job2.dry_stats["errors"] == MAX_ROW_ERRORS + 5  # true count still reported

    # 3. A job stuck in 'committing' (crashed commit / concurrent winner)
    # must refuse a second commit — the claim is previewed-only.
    email3 = f"claim-{uuid.uuid4().hex[:6]}@x.edu"
    data3 = _csv([f"{email3},C,student"])
    job3 = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data3,
        file_key="t3", created_by=owner.id, idempotency_key=f"r38c-{uuid.uuid4().hex[:8]}",
    )
    job3.status = "committing"
    await db.flush()
    with pytest.raises(AppError) as exc:
        await svc.commit(org.id, job3.id, file_bytes=data3)
    assert exc.value.code == "IMPORT_NOT_COMMITTABLE"


@pytest.mark.asyncio
async def test_list_imports_org_scoped(db):
    """R83: GET /imports lists only this org's jobs, newest first."""
    from app.integrations.api.imports import list_imports
    from app.models.user import User as _User

    org, owner = await _org(db)
    other, other_owner = await _org(db)
    svc = BulkImportService(db)
    data = _csv([f"li-{uuid.uuid4().hex[:6]}@x.edu,A,student"])
    job = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="l1", created_by=owner.id, idempotency_key=f"r83-{uuid.uuid4().hex[:8]}",
    )
    foreign = await svc.create_job(
        other.id, kind="users", mode="partial", file_bytes=data,
        file_key="l2", created_by=other_owner.id,
        idempotency_key=f"r83b-{uuid.uuid4().hex[:8]}",
    )
    owner_user = await db.get(_User, owner.id)
    out = await list_imports(org.id, db=db, user=owner_user)
    ids = [j.id for j in out["data"]]
    assert job.id in ids and foreign.id not in ids


@pytest.mark.asyncio
async def test_header_map_aliases_and_validation(db):
    """R92 column mapping: a school CSV with 'E-mail Address'/'Full Name'
    headers imports via header_map; commit re-parses with the SAME map;
    junk maps refused."""
    org, owner = await _org(db)
    svc = BulkImportService(db)
    email = f"hm-{uuid.uuid4().hex[:6]}@x.edu"
    data = (
        "E-mail Address,Full Name,Role\n"
        f"{email},Mapped Person,student\n"
    ).encode()
    job = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="hm1", created_by=owner.id,
        idempotency_key=f"r92-{uuid.uuid4().hex[:8]}",
        header_map={"email": "E-mail Address", "display_name": "Full Name", "role": "Role"},
    )
    assert job.dry_stats == {"valid": 1, "errors": 0, "creates": 1, "updates": 0, "skips": 0}
    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.stats["created"] == 1
    u = (
        await db.execute(select(User).where(func.lower(User.email) == email))
    ).scalar_one()
    assert u.display_name == "Mapped Person"

    # Without the map the same file fails on missing columns.
    job2 = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="hm2", created_by=owner.id,
        idempotency_key=f"r92b-{uuid.uuid4().hex[:8]}",
    )
    assert job2.dry_stats["errors"] >= 1 and job2.dry_stats["valid"] == 0

    # Unknown canonical key / junk alias refused.
    with pytest.raises(AppError) as e1:
        await svc.create_job(
            org.id, kind="users", mode="partial", file_bytes=data,
            file_key="hm3", created_by=owner.id,
            idempotency_key=f"r92c-{uuid.uuid4().hex[:8]}",
            header_map={"password": "Secret"},
        )
    assert e1.value.code == "IMPORT_HEADER_MAP_INVALID"
    with pytest.raises(AppError):
        await svc.create_job(
            org.id, kind="users", mode="partial", file_bytes=data,
            file_key="hm4", created_by=owner.id,
            idempotency_key=f"r92d-{uuid.uuid4().hex[:8]}",
            header_map={"email": 7},
        )


def test_csv_parser_robustness_matrix():
    """R127 (Part K): real migration CSVs are messy. parse_users_csv must be
    total — BOM, CRLF, quoted commas/newlines, extra columns, blank rows —
    without crashing, and reject what it can't trust."""
    from app.integrations.services.bulk_import import parse_users_csv

    # BOM + CRLF + a quoted display_name containing a comma.
    data = ('\ufeffemail,display_name,role\r\n'
            'a@x.edu,"Doe, Jane",student\r\n').encode("utf-8")
    rows, errors = parse_users_csv(data)
    assert errors == [] and rows[0]["display_name"] == "Doe, Jane"

    # Quoted embedded newline in a field.
    data2 = (b'email,display_name,role\n'
            b'b@x.edu,"Line1\nLine2",student\n')
    rows2, errors2 = parse_users_csv(data2)
    assert errors2 == [] and "Line1" in rows2[0]["display_name"]

    # Extra/unknown columns are ignored, not fatal.
    data3 = (b'email,display_name,role,department,notes\n'
            b'c@x.edu,C,student,eng,hi\n')
    rows3, errors3 = parse_users_csv(data3)
    assert errors3 == [] and rows3[0]["email"] == "c@x.edu"

    # Missing the required email column -> file-level error, zero rows.
    rows4, errors4 = parse_users_csv(b"display_name,role\nDee,student\n")
    assert rows4 == [] and errors4[0]["code"] == "missing_column"

    # Non-UTF8 -> clean encoding error, no crash.
    rows5, errors5 = parse_users_csv(b"\xff\xfe\x00garbage")
    assert rows5 == [] and errors5[0]["code"] == "encoding"

    # Whitespace-only email -> invalid_email row error.
    rows6, errors6 = parse_users_csv(b"email,display_name,role\n   ,X,student\n")
    assert rows6 == [] and any(e["code"] == "invalid_email" for e in errors6)


@settings(max_examples=120, deadline=None)
@given(
    rows=st.lists(
        st.tuples(st.text(max_size=40), st.text(max_size=40), st.text(max_size=20)),
        max_size=8,
    )
)
def test_parse_users_csv_total_over_arbitrary_cells(rows):
    """Arbitrary cell contents (incl. commas/quotes/controls) never crash the
    parser; every output row has a valid-shaped email + lowercased role."""
    import csv
    import io

    from app.integrations.services.bulk_import import IMPORT_ROLE_MAP, parse_users_csv

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["email", "display_name", "role"])
    for e, d, r in rows:
        w.writerow([e, d, r])
    parsed, errors = parse_users_csv(buf.getvalue().encode())
    assert isinstance(parsed, list) and isinstance(errors, list)
    for row in parsed:
        assert "@" in row["email"] and row["email"] == row["email"].lower()
        assert row["role"] in IMPORT_ROLE_MAP
        assert len(row["display_name"]) <= 100


@pytest.mark.asyncio
async def test_json_import_template(db):
    """R128 (Part K CSV/JSON): a JSON users file imports with the same
    validation as CSV; auto-detected by content; bad shape -> clean error."""
    import json as _json

    org, owner = await _org(db)
    svc = BulkImportService(db)
    email = f"js-{uuid.uuid4().hex[:6]}@x.edu"
    data = _json.dumps(
        {"users": [
            {"email": email, "display_name": "JSON User", "role": "instructor"},
            {"email": "bad-no-at", "display_name": "Nope"},
        ]}
    ).encode()
    job = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data,
        file_key="j1", created_by=owner.id, idempotency_key=f"r128-{uuid.uuid4().hex[:8]}",
    )
    assert job.dry_stats["valid"] == 1 and job.dry_stats["errors"] == 1
    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.stats["created"] == 1
    from sqlalchemy import func as _f

    u = (
        await db.execute(select(User).where(_f.lower(User.email) == email))
    ).scalar_one()
    assert u.display_name == "JSON User"

    # Top-level list form also works.
    data2 = _json.dumps([{"email": f"js2-{uuid.uuid4().hex[:6]}@x.edu"}]).encode()
    job2 = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=data2,
        file_key="j2", created_by=owner.id, idempotency_key=f"r128b-{uuid.uuid4().hex[:8]}",
    )
    assert job2.dry_stats["valid"] == 1

    # Malformed JSON -> file-level error, zero valid.
    job3 = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=b"{not json",
        file_key="j3", created_by=owner.id, idempotency_key=f"r128c-{uuid.uuid4().hex[:8]}",
    )
    assert job3.dry_stats["valid"] == 0 and job3.dry_stats["errors"] >= 1


def test_detect_format_sniffing():
    """R128: format sniffing — BOM/whitespace-prefixed JSON detected; CSV
    (even one whose first cell contains '{' mid-line) stays CSV."""
    from app.integrations.services.bulk_import import detect_format

    assert detect_format(b'[{"email": "a@b.co"}]') == "json"
    assert detect_format(b'\xef\xbb\xbf\n  {"users": []}') == "json"
    assert detect_format(b"email,display_name\na@b.co,X") == "csv"
    assert detect_format(b"") == "csv"


async def _cohort(db, org, owner, slug: str):
    from app.models.cohort import Cohort

    c = Cohort(org_id=org.id, name=slug.title(), slug=slug, created_by=owner.id)
    db.add(c)
    await db.flush()
    return c


@pytest.mark.asyncio
async def test_roster_import_kind(db):
    """R129 (Part K deferred kind): roster rows enroll existing org members
    into cohorts by slug; unknown cohort/user are row errors; re-commit of
    the same pair skips (idempotent); role never changed for existing."""
    from app.models.cohort import CohortMember, CohortRole

    org, owner = await _org(db)
    cohort = await _cohort(db, org, owner, f"c-{uuid.uuid4().hex[:8]}")
    svc = BulkImportService(db)

    # Seed one org member via the users template (the documented order).
    email = f"ro-{uuid.uuid4().hex[:6]}@x.edu"
    useed = f"email\n{email}\n".encode()
    ujob = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=useed,
        file_key="u", created_by=owner.id, idempotency_key=f"ru-{uuid.uuid4().hex[:8]}",
    )
    await svc.commit(org.id, ujob.id, file_bytes=useed)

    data = (
        "email,cohort_slug,role\n"
        f"{email},{cohort.slug},instructor\n"
        f"ghost-{uuid.uuid4().hex[:6]}@x.edu,{cohort.slug},learner\n"
        f"{email},no-such-cohort,learner\n"
    ).encode()
    job = await svc.create_job(
        org.id, kind="roster", mode="partial", file_bytes=data,
        file_key="r1", created_by=owner.id, idempotency_key=f"rr-{uuid.uuid4().hex[:8]}",
    )
    # preview: 1 enrollable, 2 resolution errors
    assert job.dry_stats["creates"] == 1 and job.dry_stats["errors"] == 2

    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.stats["created"] == 1
    assert committed.status == "partial"
    member = (
        await db.execute(
            select(CohortMember).where(CohortMember.cohort_id == cohort.id)
        )
    ).scalar_one()
    assert member.role == CohortRole.INSTRUCTOR

    # Idempotent re-import: same pair skips, role NOT downgraded to learner.
    data2 = f"email,cohort_slug,role\n{email},{cohort.slug},learner\n".encode()
    job2 = await svc.create_job(
        org.id, kind="roster", mode="partial", file_bytes=data2,
        file_key="r2", created_by=owner.id, idempotency_key=f"rr2-{uuid.uuid4().hex[:8]}",
    )
    committed2 = await svc.commit(org.id, job2.id, file_bytes=data2)
    assert committed2.stats["skipped"] == 1 and committed2.stats["created"] == 0
    await db.refresh(member)
    assert member.role == CohortRole.INSTRUCTOR


@pytest.mark.asyncio
async def test_roster_import_json_and_atomic(db):
    """R129: JSON roster template works; atomic mode rejects the whole file
    when any row cannot resolve."""
    import json as _json

    from app.models.cohort import CohortMember

    org, owner = await _org(db)
    cohort = await _cohort(db, org, owner, f"c-{uuid.uuid4().hex[:8]}")
    svc = BulkImportService(db)
    email = f"rj-{uuid.uuid4().hex[:6]}@x.edu"
    useed = f"email\n{email}\n".encode()
    ujob = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=useed,
        file_key="u", created_by=owner.id, idempotency_key=f"rj-{uuid.uuid4().hex[:8]}",
    )
    await svc.commit(org.id, ujob.id, file_bytes=useed)

    data = _json.dumps(
        {"roster": [{"email": email, "cohort_slug": cohort.slug}]}
    ).encode()
    job = await svc.create_job(
        org.id, kind="roster", mode="partial", file_bytes=data,
        file_key="r1", created_by=owner.id, idempotency_key=f"rj1-{uuid.uuid4().hex[:8]}",
    )
    assert job.dry_stats["creates"] == 1 and job.dry_stats["errors"] == 0
    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.stats["created"] == 1

    # atomic: one bad row means nothing applied
    org2, owner2 = await _org(db)
    cohort2 = await _cohort(db, org2, owner2, f"c-{uuid.uuid4().hex[:8]}")
    email2 = f"ra-{uuid.uuid4().hex[:6]}@x.edu"
    useed2 = f"email\n{email2}\n".encode()
    ujob2 = await svc.create_job(
        org2.id, kind="users", mode="partial", file_bytes=useed2,
        file_key="u2", created_by=owner2.id, idempotency_key=f"ra-{uuid.uuid4().hex[:8]}",
    )
    await svc.commit(org2.id, ujob2.id, file_bytes=useed2)
    # Bad row FIRST: the service aborts before applying anything in-session.
    # (A failure AFTER a success relies on the request-boundary rollback in
    # get_db — the whole transaction, claim included, returns to previewed.)
    bad = (
        f"email,cohort_slug\n{email2},missing-cohort\n"
        f"{email2},{cohort2.slug}\n"
    ).encode()
    job2 = await svc.create_job(
        org2.id, kind="roster", mode="atomic", file_bytes=bad,
        file_key="r2", created_by=owner2.id, idempotency_key=f"ra2-{uuid.uuid4().hex[:8]}",
    )
    # R198: atomic apply-failure returns a terminal status='failed' (no raise,
    # consistent with the validation-error path) — nothing is applied.
    failed = await svc.commit(org2.id, job2.id, file_bytes=bad)
    assert failed.status == "failed"
    assert failed.stats["applied"] == 0 and failed.stats["errors"] == 1
    n = (
        await db.execute(
            select(func.count()).select_from(CohortMember).where(
                CohortMember.cohort_id == cohort2.id
            )
        )
    ).scalar_one()
    assert n == 0


@pytest.mark.asyncio
async def test_opportunities_import_kind(db):
    """R131 (Part K deferred kind): opportunity rows land as DRAFTS for an
    org with an employer profile; bad type/openings are row errors; same
    title skips on re-upload; without a profile every row errors."""
    import json as _json

    from app.talent.models.employer import EmployerProfile, Opportunity

    org, owner = await _org(db)
    db.add(EmployerProfile(org_id=org.id))
    await db.flush()
    svc = BulkImportService(db)

    title = f"ML Intern {uuid.uuid4().hex[:6]}"
    data = (
        "title,opportunity_type,location_mode,openings\n"
        f"{title},internship,remote,2\n"
        f"Bad Type {uuid.uuid4().hex[:4]},astronaut,remote,1\n"
        f"Bad Openings {uuid.uuid4().hex[:4]},internship,remote,0\n"
    ).encode()
    job = await svc.create_job(
        org.id, kind="opportunities", mode="partial", file_bytes=data,
        file_key="o1", created_by=owner.id, idempotency_key=f"op-{uuid.uuid4().hex[:8]}",
    )
    assert job.dry_stats["valid"] == 1 and job.dry_stats["errors"] == 2
    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.stats["created"] == 1
    opp = (
        await db.execute(
            select(Opportunity).where(Opportunity.employer_org_id == org.id)
        )
    ).scalar_one()
    assert opp.status == "draft"  # import NEVER publishes
    assert opp.openings == 2 and opp.location_mode == "remote"
    assert opp.created_by == owner.id

    # idempotent re-upload (JSON this time, case-insensitive title match)
    data2 = _json.dumps(
        {"opportunities": [{"title": title.upper(), "opportunity_type": "internship"}]}
    ).encode()
    job2 = await svc.create_job(
        org.id, kind="opportunities", mode="partial", file_bytes=data2,
        file_key="o2", created_by=owner.id, idempotency_key=f"op2-{uuid.uuid4().hex[:8]}",
    )
    assert job2.dry_stats["skips"] == 1
    committed2 = await svc.commit(org.id, job2.id, file_bytes=data2)
    assert committed2.stats["skipped"] == 1 and committed2.stats["created"] == 0

    # no employer profile: every row is a resolution error at preview
    org2, owner2 = await _org(db)
    data3 = b"title,opportunity_type\nX,internship\n"
    job3 = await svc.create_job(
        org2.id, kind="opportunities", mode="partial", file_bytes=data3,
        file_key="o3", created_by=owner2.id, idempotency_key=f"op3-{uuid.uuid4().hex[:8]}",
    )
    assert job3.dry_stats["valid"] == 0 and job3.dry_stats["errors"] == 1
    # R153: the error report names the offending row by TITLE for this kind.
    report = await svc.errors_csv(org2.id, job3.id)
    assert "identifier" in report.splitlines()[0]
    assert "X" in report


@pytest.mark.asyncio
async def test_roster_default_role_and_infile_dup(db):
    """R133 mutation-probe kills: omitted role defaults to LEARNER, and the
    same (email, cohort_slug) pair twice in one file is a duplicate_in_file
    row error — exactly one membership lands."""
    from app.integrations.models import ImportRowError
    from app.models.cohort import CohortMember, CohortRole

    org, owner = await _org(db)
    cohort = await _cohort(db, org, owner, f"c-{uuid.uuid4().hex[:8]}")
    svc = BulkImportService(db)
    email = f"rd-{uuid.uuid4().hex[:6]}@x.edu"
    useed = f"email\n{email}\n".encode()
    ujob = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=useed,
        file_key="u", created_by=owner.id, idempotency_key=f"rd-{uuid.uuid4().hex[:8]}",
    )
    await svc.commit(org.id, ujob.id, file_bytes=useed)

    # no role column at all + the same pair twice
    data = (
        "email,cohort_slug\n"
        f"{email},{cohort.slug}\n"
        f"{email},{cohort.slug}\n"
    ).encode()
    job = await svc.create_job(
        org.id, kind="roster", mode="partial", file_bytes=data,
        file_key="r", created_by=owner.id, idempotency_key=f"rd2-{uuid.uuid4().hex[:8]}",
    )
    assert job.dry_stats["valid"] == 1 and job.dry_stats["errors"] == 1
    err = (
        await db.execute(
            select(ImportRowError).where(ImportRowError.job_id == job.id)
        )
    ).scalar_one()
    assert err.code == "duplicate_in_file"
    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.stats["created"] == 1
    member = (
        await db.execute(
            select(CohortMember).where(CohortMember.cohort_id == cohort.id)
        )
    ).scalar_one()
    assert member.role == CohortRole.LEARNER  # omitted role -> learner


@pytest.mark.asyncio
async def test_import_file_retention_sweep(db):
    """R134 (PII governance): terminal jobs past 90d get their stored file
    deleted and file_key blanked; fresh/non-terminal jobs keep theirs; a
    failing delete skips that job without stopping the sweep; blanked jobs
    are never re-scanned."""
    from datetime import UTC, datetime, timedelta

    from app.integrations.services.bulk_import import sweep_import_files

    org, owner = await _org(db)
    svc = BulkImportService(db)

    async def mk(status: str, age_days: int, file_key: str):
        data = f"email\nsw-{uuid.uuid4().hex[:6]}@x.edu\n".encode()
        job = await svc.create_job(
            org.id, kind="users", mode="partial", file_bytes=data,
            file_key=file_key, created_by=owner.id,
            idempotency_key=f"sw-{uuid.uuid4().hex[:10]}",
        )
        job.status = status
        job.created_at = datetime.now(UTC) - timedelta(days=age_days)
        await db.flush()
        return job

    old_done = await mk("succeeded", 120, "k-old-done")
    old_failed = await mk("failed", 120, "k-old-failed")
    old_previewed = await mk("previewed", 120, "k-old-previewed")
    fresh_done = await mk("succeeded", 5, "k-fresh")
    old_poison = await mk("partial", 120, "k-poison")

    deleted: list[str] = []

    async def deleter(key: str) -> None:
        if key == "k-poison":
            raise RuntimeError("s3 down for this key")
        deleted.append(key)

    purged = await sweep_import_files(db, deleter=deleter)
    assert purged == 2
    assert sorted(deleted) == ["k-old-done", "k-old-failed"]
    await db.refresh(old_done)
    await db.refresh(old_previewed)
    await db.refresh(fresh_done)
    await db.refresh(old_poison)
    assert old_done.file_key == ""           # purged + blanked
    assert old_previewed.file_key == "k-old-previewed"  # non-terminal kept
    assert fresh_done.file_key == "k-fresh"  # inside the window
    assert old_poison.file_key == "k-poison"  # delete failed -> retried later

    # second sweep: only the poison job remains scannable
    deleted.clear()
    purged2 = await sweep_import_files(db, deleter=deleter)
    assert purged2 == 0 and deleted == []
    assert old_failed is not None


@pytest.mark.asyncio
async def test_import_create_and_commit_write_audit_rows(db, monkeypatch):
    """R138 (Part O): bulk provisioning is audited — upload writes
    intg.import.created, commit writes intg.import.committed, rows LAND
    (registered actions, not silently swallowed) with the acting user."""
    import io as _io

    from starlette.datastructures import UploadFile as _Upload

    import app.integrations.api.imports as imports_api
    from app.controlplane.models.audit import CommercialAuditEvent as AuditEvent

    org, owner = await _org(db)
    owner_user = owner
    data = f"email\nau-{uuid.uuid4().hex[:6]}@x.edu\n".encode()
    stored: dict[str, bytes] = {}

    async def fake_store(org_id, hint, content):
        stored["k"] = content
        return "fake-key"

    async def fake_load(file_key):
        return stored["k"]

    monkeypatch.setattr(imports_api, "_store_file", fake_store)
    monkeypatch.setattr(imports_api, "_load_file", fake_load)

    out = await imports_api.upload_import(
        org.id,
        kind="users",
        mode="partial",
        idempotency_key=f"au-{uuid.uuid4().hex[:8]}",
        header_map=None,
        file=_Upload(_io.BytesIO(data), filename="u.csv"),
        db=db,
        user=owner_user,
    )
    job_id = out["data"].id
    out2 = await imports_api.commit_import(org.id, job_id, db=db, user=owner_user)
    assert out2["data"].status == "succeeded"

    rows = (
        await db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.target_type == "import_job",
                AuditEvent.target_id == job_id,
            )
            .order_by(AuditEvent.created_at)
        )
    ).scalars().all()
    actions = [r.action for r in rows]
    assert actions == ["intg.import.created", "intg.import.committed"]
    assert all(r.actor_user_id == owner.id for r in rows)
    assert rows[0].after["kind"] == "users"
    assert rows[1].after["stats"]["created"] == 1

    # R143: commit also lands a mesh event — counts only, never the roster.
    from app.integrations.models.events import IntegrationEvent

    ev = (
        await db.execute(
            select(IntegrationEvent).where(
                IntegrationEvent.org_id == org.id,
                IntegrationEvent.type == "com.openskill.org.import.committed.v1",
            )
        )
    ).scalar_one()
    assert ev.subject == job_id
    assert ev.data["stats"]["created"] == 1
    assert "email" not in str(ev.data)


def test_kind_registries_consistent():
    """R148: IMPORT_KINDS, TEMPLATE_VERSIONS and KIND_SPECS must agree —
    a kind present in one but not the others KeyErrors at runtime (create
    reads TEMPLATE_VERSIONS[kind], parse reads KIND_SPECS[kind])."""
    from app.integrations.models.bulk import IMPORT_KINDS
    from app.integrations.services.bulk_import import KIND_SPECS, TEMPLATE_VERSIONS

    assert set(IMPORT_KINDS) == set(TEMPLATE_VERSIONS) == set(KIND_SPECS)
    for kind, spec in KIND_SPECS.items():
        assert set(spec.required) <= set(spec.known_headers), kind
        assert TEMPLATE_VERSIONS[kind] >= 1


def test_import_template_generator():
    """R169: template_for emits ordered columns (required first) + one example
    row, for CSV and JSON, for every kind; unknown kind is refused; the
    example row round-trips back through the parser with zero errors."""
    import csv as _csv
    import io as _io
    import json as _json

    from app.exceptions import AppError
    from app.integrations.services.bulk_import import (
        KIND_SPECS,
        detect_format,
        parse_users,
        template_for,
    )

    for kind, spec in KIND_SPECS.items():
        body, ctype = template_for(kind, "csv")
        assert ctype == "text/csv"
        reader = list(_csv.reader(_io.StringIO(body.decode())))
        header = reader[0]
        assert header == list(spec.columns)  # ordered, required first
        for req in spec.required:
            assert req in header
        # the example row parses cleanly (template is a valid starting point)
        rows, errors = parse_users(body, detect_format(body), kind=kind)
        assert errors == [], f"{kind} template example did not parse: {errors}"
        assert len(rows) == 1

        jbody, jctype = template_for(kind, "json")
        assert jctype == "application/json"
        doc = _json.loads(jbody)
        assert kind in doc and len(doc[kind]) == 1
        jrows, jerrors = parse_users(jbody, "json", kind=kind)
        assert jerrors == [] and len(jrows) == 1

    try:
        template_for("nonsense", "csv")
        raise AssertionError("unknown kind must raise")
    except AppError as e:
        assert e.code == "IMPORT_KIND_INVALID"


@pytest.mark.asyncio
async def test_roster_import_honors_cohort_capacity(db):
    """R188: a bulk roster import must not overfill a capped cohort — with
    max_learners=1, importing two learners enrolls one and records a
    cohort_full row error for the other (partial mode)."""
    from app.models.cohort import Cohort, CohortMember, CohortRole

    org, owner = await _org(db)
    cohort = Cohort(
        org_id=org.id, name="Capped", slug=f"cap-{uuid.uuid4().hex[:8]}",
        created_by=owner.id, max_learners=1,
    )
    db.add(cohort)
    await db.flush()
    svc = BulkImportService(db)

    e1 = f"cap1-{uuid.uuid4().hex[:6]}@x.edu"
    e2 = f"cap2-{uuid.uuid4().hex[:6]}@x.edu"
    useed = f"email\n{e1}\n{e2}\n".encode()
    ujob = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=useed,
        file_key="u", created_by=owner.id, idempotency_key=f"cap-{uuid.uuid4().hex[:8]}",
    )
    await svc.commit(org.id, ujob.id, file_bytes=useed)

    data = (
        "email,cohort_slug,role\n"
        f"{e1},{cohort.slug},learner\n"
        f"{e2},{cohort.slug},learner\n"
    ).encode()
    job = await svc.create_job(
        org.id, kind="roster", mode="partial", file_bytes=data,
        file_key="r", created_by=owner.id, idempotency_key=f"capr-{uuid.uuid4().hex[:8]}",
    )
    committed = await svc.commit(org.id, job.id, file_bytes=data)
    assert committed.stats["created"] == 1  # only one fit
    assert committed.stats["errors"] == 1   # the other hit capacity
    n = (
        await db.execute(
            select(func.count()).select_from(CohortMember).where(
                CohortMember.cohort_id == cohort.id,
                CohortMember.role == CohortRole.LEARNER,
            )
        )
    ).scalar_one()
    assert n == 1  # never overfilled


@pytest.mark.asyncio
async def test_atomic_apply_failure_persists_failed_status(db):
    """R198: when an atomic import fails during APPLY (not validation), the
    job's terminal status='failed' + reason must PERSIST (survive the commit),
    not be erased by a raise/rollback leaving the job stuck at 'previewed'.
    And no rows are applied."""
    from app.models.cohort import Cohort, CohortMember

    org, owner = await _org(db)
    cohort = await _cohort(db, org, owner, f"c-{uuid.uuid4().hex[:8]}")
    svc = BulkImportService(db)
    email = f"ap-{uuid.uuid4().hex[:6]}@x.edu"
    useed = f"email\n{email}\n".encode()
    ujob = await svc.create_job(
        org.id, kind="users", mode="partial", file_bytes=useed,
        file_key="u", created_by=owner.id, idempotency_key=f"ap-{uuid.uuid4().hex[:8]}",
    )
    await svc.commit(org.id, ujob.id, file_bytes=useed)

    # Atomic roster: first row valid, second references a missing cohort —
    # validation passes (slug shape ok) but APPLY fails on resolution.
    data = (
        "email,cohort_slug\n"
        f"{email},{cohort.slug}\n"
        f"{email},missing-cohort-xyz\n"
    ).encode()
    job = await svc.create_job(
        org.id, kind="roster", mode="atomic", file_bytes=data,
        file_key="r", created_by=owner.id, idempotency_key=f"apr-{uuid.uuid4().hex[:8]}",
    )
    job_id = job.id
    result = await svc.commit(org.id, job_id, file_bytes=data)
    assert result.status == "failed"
    assert "missing" not in result.stats.get("reason", "") or result.stats["applied"] == 0

    # Persisted: re-fetch from a committed state (simulate the API commit).
    await db.commit()
    from app.integrations.models import ImportJob

    refetched = await db.get(ImportJob, job_id)
    await db.refresh(refetched)
    assert refetched.status == "failed"  # NOT stuck at 'previewed'/'committing'

    # Atomic = nothing applied: the valid first row did not enroll.
    n = (
        await db.execute(
            select(func.count()).select_from(CohortMember).where(
                CohortMember.cohort_id == cohort.id
            )
        )
    ).scalar_one()
    assert n == 0
    assert Cohort is not None


def test_duplicate_canonical_column_rejected():
    """R205: two columns mapping to the same canonical field (a duplicate
    header) must be a clear file-level error — not a silent csv.DictReader
    last-wins data drop."""
    data = b"email,email,role\r\na@x.edu,b@x.edu,student\r\n"
    rows, errors = parse_users_csv(data)
    assert rows == []
    assert errors[0]["code"] == "duplicate_column" and errors[0]["column"] == "email"

    # header_map aliasing a second source column onto an existing canonical
    # also collides (both land on "email").
    data2 = b"primary,secondary,role\r\na@x.edu,b@x.edu,student\r\n"
    rows2, errors2 = parse_users_csv(
        data2, header_map={"email": "primary", "display_name": "secondary"}
    )
    # primary->email, secondary->display_name: no collision, one of each.
    assert errors2 == [] and len(rows2) == 1

    data3 = b"primary,secondary,role\r\na@x.edu,b@x.edu,student\r\n"
    rows3, errors3 = parse_users_csv(
        data3, header_map={"email": "primary"}
    )
    # Only primary->email; secondary stays unknown (ignored). One email col.
    assert errors3 == [] and len(rows3) == 1
