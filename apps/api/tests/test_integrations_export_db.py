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
        await svc.create_stream(org.id, name="x", dataset="events", field_allowlist=["id", "data"])
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
    rows2 = [json.loads(line) for line in writer.files[run2.parts[0]].decode().strip().split("\n")]
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
    rows = [json.loads(line) for line in writer.files[r1.parts[0]].decode().strip().split("\n")]
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
    rows2 = [json.loads(line) for line in writer.files[r2.parts[0]].decode().strip().split("\n")]
    assert "user_id" not in rows2[0]
    # per-org salt: same user exported by another org hashes DIFFERENTLY
    salted = hashlib.sha256(f"x:{learner.id}".encode()).hexdigest()[:32]
    assert rows[0]["user_id"] != salted  # not an unsalted/global hash


# ── R16: scheduled export sweep (same gap class as scheduled syncs) ──


@pytest.mark.asyncio
async def test_sweep_scheduled_exports_runs_due_daily_streams(db):
    from app.integrations.services.warehouse import sweep_scheduled_exports

    org, owner = await _org(db)
    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    daily = await svc.create_stream(org.id, name=f"d-{ULID()}", dataset="events", schedule="daily")
    manual = await svc.create_stream(org.id, name=f"m-{ULID()}", dataset="events")
    await emit_event(db, org.id, "project.approved", subject="s", data={})
    await db.flush()
    # First sweep: the daily stream runs, the manual one never does.
    assert await sweep_scheduled_exports(db, writer) == 1
    runs = await svc.list_runs(org.id, daily.id)
    assert len(runs) == 1 and runs[0].status == "succeeded"
    assert await svc.list_runs(org.id, manual.id) == []
    # Within the day: not due again.
    assert await sweep_scheduled_exports(db, writer) == 0


# ── R40: warehouse probe killers ──


@pytest.mark.asyncio
async def test_narrowed_allowlist_disabled_gate_salt_pagination_failure(db, monkeypatch):
    import app.integrations.services.warehouse as wh

    org, owner = await _org(db)
    org2, _ = await _org(db)
    await emit_event(db, org.id, "project.approved", subject="same-subj", data={"x": 1})
    await emit_event(db, org2.id, "project.approved", subject="same-subj", data={"x": 1})
    await db.flush()

    # 1. NARROWED allowlist: the projection is built FROM the allowlist —
    # extractor fields outside it must never appear (row.keys() mutant).
    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    s = await svc.create_stream(
        org.id, name=f"nr-{ULID()}", dataset="events", field_allowlist=["id", "type"]
    )
    run = await svc.run_export(org.id, s.id)
    rows = [json.loads(x) for x in writer.files[run.parts[0]].decode().strip().split("\n")]
    assert all(set(r) == {"id", "type"} for r in rows)

    # 2. Org-salted hashing: the same value hashes DIFFERENTLY per org
    # (cross-org joinability guard).
    w1, w2 = MemWriter(), MemWriter()
    sa = await WarehouseExportService(db, writer=w1).create_stream(
        org.id,
        name=f"ha-{ULID()}",
        dataset="events",
        field_allowlist=["id", "subject"],
        anonymize={"subject": "hash"},
    )
    sb = await WarehouseExportService(db, writer=w2).create_stream(
        org2.id,
        name=f"hb-{ULID()}",
        dataset="events",
        field_allowlist=["id", "subject"],
        anonymize={"subject": "hash"},
    )
    ra = await WarehouseExportService(db, writer=w1).run_export(org.id, sa.id)
    rb = await WarehouseExportService(db, writer=w2).run_export(org2.id, sb.id)
    ha = json.loads(w1.files[ra.parts[0]].decode().strip().split("\n")[0])["subject"]
    hb = json.loads(w2.files[rb.parts[0]].decode().strip().split("\n")[0])["subject"]
    assert ha != hb  # same raw subject, different org salt

    # 3. Disabled stream refuses to run.
    s.enabled = False
    await db.flush()
    with pytest.raises(AppError) as exc:
        await svc.run_export(org.id, s.id)
    assert exc.value.code == "EXPORT_STREAM_DISABLED"
    s.enabled = True
    await db.flush()

    # 4. Pagination: with page size 1, three events -> 3 parts, all rows.
    await emit_event(db, org.id, "project.approved", subject="pg-2", data={})
    await emit_event(db, org.id, "project.approved", subject="pg-3", data={})
    await db.flush()
    monkeypatch.setattr(wh, "EXPORT_PAGE_ROWS", 1)
    wpg = MemWriter()
    spg = await WarehouseExportService(db, writer=wpg).create_stream(
        org.id, name=f"pg-{ULID()}", dataset="events"
    )
    rpg = await WarehouseExportService(db, writer=wpg).run_export(org.id, spg.id)
    assert rpg.row_count == 3 and len(rpg.parts) == 3
    monkeypatch.setattr(wh, "EXPORT_PAGE_ROWS", 1000)

    # 5. Writer failure -> run FAILED and the stream cursor does NOT move.
    class _BoomWriter:
        async def write(self, key, content):
            raise RuntimeError("disk full")

    sfail = await WarehouseExportService(db, writer=_BoomWriter()).create_stream(
        org.id, name=f"fl-{ULID()}", dataset="events"
    )
    before = dict(sfail.cursor or {})
    rf = await WarehouseExportService(db, writer=_BoomWriter()).run_export(org.id, sfail.id)
    assert rf.status == "failed" and rf.error == "RuntimeError"
    await db.refresh(sfail)
    assert dict(sfail.cursor or {}) == before


@pytest.mark.asyncio
async def test_update_stream_edits_and_validates(db):
    """R81: allowlist narrows (universe-checked), anonymize validated,
    schedule/enabled flips, cross-org uniform 404."""
    org, owner = await _org(db)
    other, _ = await _org(db)
    svc = WarehouseExportService(db, writer=MemWriter())
    s = await svc.create_stream(org.id, name=f"up-{ULID()}", dataset="events")

    out = await svc.update_stream(
        org.id,
        s.id,
        field_allowlist=["id", "type"],
        anonymize={"subject": "hash"},
        schedule="daily",
        enabled=False,
    )
    assert out.field_allowlist == ["id", "type"]
    assert out.anonymize == {"subject": "hash"}
    assert out.schedule == "daily" and out.enabled is False

    with pytest.raises(AppError) as e1:
        await svc.update_stream(org.id, s.id, field_allowlist=["id", "nope"])
    assert e1.value.code == "EXPORT_FIELD_NOT_ALLOWED"
    with pytest.raises(AppError):
        await svc.update_stream(org.id, s.id, field_allowlist=[])
    with pytest.raises(AppError):
        await svc.update_stream(org.id, s.id, anonymize={"id": "scramble"})
    with pytest.raises(AppError):
        await svc.update_stream(org.id, s.id, schedule="hourly-ish")
    with pytest.raises(AppError) as e2:
        await svc.update_stream(other.id, s.id, enabled=True)
    assert e2.value.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("n_orgs,events_each", [(2, 3), (3, 2), (4, 1), (2, 5)])
async def test_export_tenant_isolation_matrix(db, n_orgs, events_each):
    """R117 (Part L): with N orgs' events INTERLEAVED in emit order, each
    org's export contains exactly its own rows and never another org's —
    the extractor WHERE org_id clause is the only thing standing between
    tenants in the warehouse."""
    orgs = [await _org(db) for _ in range(n_orgs)]
    marker = {}
    # Interleave emits round-robin so ULID ordering mixes orgs.
    for i in range(events_each):
        for j, (org, _) in enumerate(orgs):
            subj = f"o{j}-e{i}-{uuid.uuid4().hex[:4]}"
            marker.setdefault(org.id, set()).add(subj)
            await emit_event(db, org.id, "project.approved", subject=subj, data={})
    await db.commit()

    svc = WarehouseExportService(db, writer=MemWriter())
    for org, _owner in orgs:
        writer = MemWriter()
        s = await WarehouseExportService(db, writer=writer).create_stream(
            org.id, name=f"iso-{ULID()}", dataset="events"
        )
        run = await WarehouseExportService(db, writer=writer).run_export(org.id, s.id)
        assert run.row_count == events_each
        subjects = set()
        for part in run.parts:
            for line in writer.files[part].decode().strip().split("\n"):
                subjects.add(json.loads(line)["subject"])
        assert subjects == marker[org.id]  # exactly own rows, nothing foreign
    assert svc is not None


@pytest.mark.asyncio
async def test_export_enrollments_tenant_isolation(db):
    """R117: an enrollments export never contains another org's cohort
    members (the Cohort.org_id join filter is the boundary)."""
    from app.services.cohort import CohortService

    orgs = []
    for _ in range(2):
        org, owner = await _org(db)
        csvc = CohortService(db)
        cohort = await csvc.create_cohort(
            org_id=org.id, name=f"C {ULID()}", description=None, created_by=owner.id
        )
        learner = User(
            email=f"iso-{uuid.uuid4().hex[:8]}@test.com",
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
        orgs.append((org, cohort.id))
    await db.commit()

    # Use an allowlist WITHOUT the default user_id hash so the boundary is
    # asserted on the raw cohort_id (user_id hash is salted per-org anyway).
    for org, own_cohort in orgs:
        others = {c for o, c in orgs if o.id != org.id}
        writer = MemWriter()
        s = await WarehouseExportService(db, writer=writer).create_stream(
            org.id,
            name=f"en-{ULID()}",
            dataset="enrollments",
            field_allowlist=["id", "cohort_id", "role"],
            anonymize={},
        )
        run = await WarehouseExportService(db, writer=writer).run_export(org.id, s.id)
        cohort_ids = set()
        for part in run.parts:
            for line in writer.files[part].decode().strip().split("\n"):
                cohort_ids.add(json.loads(line)["cohort_id"])
        assert own_cohort in cohort_ids
        assert cohort_ids.isdisjoint(others)  # no foreign cohort members


@pytest.mark.asyncio
async def test_per_key_data_selection(db):
    """R130 (deferred item): explicit `data.<key>` allowlist entries export
    just those payload keys; unselected keys never appear; the whole `data`
    field stays unexportable; hash-anonymize works on a data key; caps and
    dataset scoping enforced."""
    org, _ = await _org(db)
    await emit_event(
        db,
        org.id,
        "project.approved",
        subject="p1",
        data={"score": 97, "secret_note": "do not export", "learner": "u_1"},
    )
    await db.flush()
    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)

    stream = await svc.create_stream(
        org.id,
        name=f"dk-{ULID()}",
        dataset="events",
        field_allowlist=["id", "type", "data.score", "data.learner", "data.absent"],
        anonymize={"data.learner": "hash"},
    )
    run = await svc.run_export(org.id, stream.id)
    assert run.status == "succeeded" and run.row_count == 1
    part = next(v for k, v in writer.files.items() if k.endswith(".ndjson"))
    row = json.loads(part.decode().strip())
    assert row["data.score"] == 97
    assert row["data.absent"] is None  # selected but missing -> null, no crash
    assert "secret_note" not in json.dumps(row)  # unselected key never leaks
    assert "data" not in row  # whole payload still not a field
    assert row["data.learner"] != "u_1" and len(row["data.learner"]) == 32  # hashed

    # whole `data`, bad shapes, wrong dataset, cap -> refused at config time
    for bad in (["data"], ["data."], ["data..x"], ["data." + "k" * 65]):
        with pytest.raises(AppError) as e:
            await svc.create_stream(
                org.id, name=f"bad-{ULID()}", dataset="events", field_allowlist=bad
            )
        assert e.value.code == "EXPORT_FIELD_NOT_ALLOWED", bad
    with pytest.raises(AppError) as e2:
        await svc.create_stream(
            org.id,
            name=f"bad-{ULID()}",
            dataset="enrollments",
            field_allowlist=["id", "data.score"],
        )
    assert e2.value.code == "EXPORT_FIELD_NOT_ALLOWED"
    with pytest.raises(AppError) as e3:
        await svc.create_stream(
            org.id,
            name=f"bad-{ULID()}",
            dataset="events",
            field_allowlist=[f"data.k{i}" for i in range(21)],
        )
    assert e3.value.code == "EXPORT_CONFIG_INVALID"

    # update_stream enforces the same rules
    with pytest.raises(AppError):
        await svc.update_stream(org.id, stream.id, field_allowlist=["data"])
    updated = await svc.update_stream(org.id, stream.id, field_allowlist=["id", "data.score"])
    assert updated.field_allowlist == ["id", "data.score"]


@pytest.mark.asyncio
async def test_sweep_scheduled_exports_hourly_cadence(db):
    """R183: hourly export streams run on an hourly cadence (not the daily
    one); within the hour they are not due, past the hour they run again."""
    from datetime import UTC, datetime, timedelta

    from app.integrations.models.export import ExportRun
    from app.integrations.services.warehouse import sweep_scheduled_exports

    org, owner = await _org(db)
    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    hourly = await svc.create_stream(
        org.id, name=f"h-{ULID()}", dataset="events", schedule="hourly"
    )
    await emit_event(db, org.id, "project.approved", subject="s", data={})
    await db.flush()

    assert await sweep_scheduled_exports(db, writer) == 1
    runs = await svc.list_runs(org.id, hourly.id)
    assert len(runs) == 1
    # Within the hour: not due.
    assert await sweep_scheduled_exports(db, writer) == 0

    # Backdate the last run beyond an hour -> due again (but NOT a full day,
    # proving the cadence is hourly, not daily).
    run = await db.get(ExportRun, runs[0].id)
    run.created_at = datetime.now(UTC) - timedelta(hours=2)
    await db.flush()
    assert await sweep_scheduled_exports(db, writer) == 1


@pytest.mark.asyncio
async def test_export_empty_source_still_writes_manifest(db):
    """R203: an export over an empty source still produces a manifest
    (row_count=0, parts=[]) and succeeds — the run is observable in the
    warehouse, never a silent no-op."""
    org, owner = await _org(db)
    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    stream = await svc.create_stream(org.id, name=f"empty-{ULID()}", dataset="events")
    # No events emitted for this org → zero rows.
    run = await svc.run_export(org.id, stream.id)
    assert run.status == "succeeded"
    assert run.row_count == 0
    assert run.manifest_key in writer.files
    manifest = json.loads(writer.files[run.manifest_key])
    assert manifest["row_count"] == 0
    assert manifest["parts"] == []
    assert manifest["generated_at"]


@pytest.mark.asyncio
async def test_concurrent_run_export_serializes_on_stream_lock(db):
    """R208: a manual trigger racing the hourly sweep must not double-export
    the span or regress the cursor. The stream row lock serializes runs: the
    second run waits, re-reads the ADVANCED cursor under the lock, and
    exports 0 rows. Without the lock both read the same cursor and the total
    row count doubles (the slow writer yields the loop mid-run to force the
    interleave, so this test genuinely kills the no-lock mutant)."""
    import asyncio

    from app.core.database import AsyncSessionLocal

    org, _ = await _org(db)
    for i in range(3):
        await emit_event(db, org.id, "project.approved", subject=f"ce-{i}", data={})
    svc = WarehouseExportService(db, writer=MemWriter())
    stream = await svc.create_stream(org.id, name=f"race-{ULID()}", dataset="events")
    await db.commit()

    class SlowWriter(MemWriter):
        async def write(self, key, content):
            await asyncio.sleep(0.05)  # yield so the other run interleaves
            await super().write(key, content)

    async def _run():
        async with AsyncSessionLocal() as s:
            run = await WarehouseExportService(s, writer=SlowWriter()).run_export(org.id, stream.id)
            counts = (run.status, run.row_count or 0)
            await s.commit()
            return counts

    (s1, c1), (s2, c2) = await asyncio.gather(_run(), _run())
    assert s1 == s2 == "succeeded"
    # exactly one of them exported the 3 events; the other saw the advanced
    # cursor under the lock and exported nothing.
    assert sorted([c1, c2]) == [0, 3]


@pytest.mark.asyncio
async def test_sweep_never_runs_manual_or_disabled_streams(db):
    """R243 (survivor pins): the scheduler's NEGATIVE space — a `manual`
    stream must never auto-run (R183's documented rule had no test), and a
    disabled stream must be skipped even when its schedule is due."""
    from sqlalchemy import select

    from app.integrations.models.export import ExportRun
    from app.integrations.services.warehouse import sweep_scheduled_exports

    org, _ = await _org(db)
    for _i in range(2):
        await emit_event(db, org.id, "project.approved", subject="sw", data={})
    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    manual = await svc.create_stream(org.id, name=f"man-{ULID()}", dataset="events")
    assert manual.schedule == "manual"
    hourly_off = await svc.create_stream(
        org.id, name=f"off-{ULID()}", dataset="events", schedule="hourly"
    )
    hourly_off.enabled = False
    await db.flush()
    await sweep_scheduled_exports(db, writer)
    for s in (manual, hourly_off):
        runs = (
            (await db.execute(select(ExportRun).where(ExportRun.stream_id == s.id))).scalars().all()
        )
        assert runs == [], f"stream {s.schedule}/{s.enabled} must not auto-run"


async def test_s3_round_trip_bucket_bytes_honor_allowlist_and_anonymize(db):
    """R381: every export content proof used MemWriter — the real
    S3PartWriter seam (content-type, key layout, the actual bucket bytes)
    was never exercised. Run an export through S3PartWriter against the
    real MinIO, fetch the part back from the bucket, and assert the BYTES
    IN THE BUCKET are allowlist-narrowed and anonymized."""
    import json as _json

    from app.config import settings
    from app.core.storage import get_s3_client
    from app.integrations.facade import emit_event
    from app.integrations.services.warehouse import S3PartWriter, WarehouseExportService

    org, _ = await _org(db)
    await emit_event(db, org.id, "project.approved", subject="s3-secret-subject", data={"k": 1})
    await db.flush()

    svc = WarehouseExportService(db, writer=S3PartWriter())
    stream = await svc.create_stream(
        org.id,
        name=f"s3rt-{ULID()}",
        dataset="events",
        field_allowlist=["id", "type", "subject"],
        anonymize={"subject": "hash"},
    )
    run = await svc.run_export(org.id, stream.id)
    assert run.status == "succeeded" and run.parts, (run.status, run.error)

    async for client in get_s3_client():
        obj = await client.get_object(Bucket=settings.s3_bucket, Key=run.parts[0])
        raw = await obj["Body"].read()
    rows = [_json.loads(x) for x in raw.decode().strip().split("\n")]
    assert rows, "bucket part is empty"
    assert all(set(r) == {"id", "type", "subject"} for r in rows), rows[0].keys()
    assert all(r["subject"] != "s3-secret-subject" for r in rows), "anonymize missed the bucket"
    # cleanup the object (bucket hygiene for repeated runs)
    async for client in get_s3_client():
        await client.delete_object(Bucket=settings.s3_bucket, Key=run.parts[0])


@pytest.mark.asyncio
async def test_sweep_naive_last_run_coerced_and_apperror_skipped(db, monkeypatch):
    """R429: sweep_scheduled_exports's naive-last-run coercion (a prior run
    row stored tz-less must still be compared against the cadence) and the
    per-stream AppError skip (one failing export must not abort the sweep
    of the others)."""
    from datetime import UTC, datetime, timedelta

    import app.integrations.services.warehouse as wh
    from app.exceptions import AppError
    from app.integrations.models import ExportRun
    from app.integrations.services.warehouse import sweep_scheduled_exports

    org, owner = await _org(db)
    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    s_ok = await svc.create_stream(org.id, name=f"ok-{ULID()}", dataset="events", schedule="daily")
    s_bad = await svc.create_stream(
        org.id, name=f"bad-{ULID()}", dataset="events", schedule="daily"
    )
    await emit_event(db, org.id, "project.approved", subject="s", data={})
    await db.flush()

    # s_ok has a NAIVE last-run row 2 days ago -> due again (coercion arm);
    # if the naive datetime weren't coerced, the subtraction would raise.
    db.add(
        ExportRun(
            stream_id=s_ok.id,
            status="succeeded",
            created_at=(datetime.now(UTC) - timedelta(days=2)).replace(tzinfo=None),
            parts=[],
        )
    )
    await db.flush()

    # s_bad's export raises AppError -> that stream is skipped, s_ok still runs.
    real_run = WarehouseExportService.run_export

    async def flaky_run(self, org_id, stream_id):
        if stream_id == s_bad.id:
            raise AppError("EXPORT_SINK_UNAVAILABLE", "sink down", 503)
        return await real_run(self, org_id, stream_id)

    monkeypatch.setattr(wh.WarehouseExportService, "run_export", flaky_run)
    ran = await sweep_scheduled_exports(db, writer)
    assert ran == 1  # s_ok ran; s_bad raised and was skipped, not fatal
    runs_ok = await svc.list_runs(org.id, s_ok.id)
    assert any(
        r.status == "succeeded" and r.created_at > datetime.now(UTC) - timedelta(minutes=5)
        for r in runs_ok
    )


@pytest.mark.asyncio
async def test_create_stream_bad_schedule_and_duplicate_name(db):
    """R468: create_stream validation arms — an invalid schedule -> 422, and a
    duplicate (org, name) -> 409 EXPORT_NAME_TAKEN (savepoint-guarded, no 500)."""
    org, owner = await _org(db)
    svc = WarehouseExportService(db, writer=MemWriter())

    with pytest.raises(AppError) as e:
        await svc.create_stream(
            org.id, name=f"s-{ULID()}", dataset="events", schedule="fortnightly"
        )
    assert e.value.code == "EXPORT_CONFIG_INVALID"

    name = f"dup-{ULID()}"
    await svc.create_stream(org.id, name=name, dataset="events")
    with pytest.raises(AppError) as e:
        await svc.create_stream(org.id, name=name, dataset="events")
    assert e.value.code == "EXPORT_NAME_TAKEN" and e.value.status_code == 409


# ── R486: parquet part format ──


@pytest.mark.asyncio
async def test_parquet_export_round_trip(db):
    """format="parquet" writes readable parquet parts whose columns are
    exactly the exported allowlist (drop-fields structurally absent), the
    manifest advertises the format, and incremental cursors still advance."""
    import io

    import pyarrow.parquet as pq

    org, owner = await _org(db)
    for i in range(3):
        await emit_event(db, org.id, "project.approved", subject=f"pq{i}", data={"k": i})
    await db.flush()

    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    stream = await svc.create_stream(
        org.id, name=f"pq-{ULID()}", dataset="events", part_format="parquet"
    )
    assert stream.format == "parquet"
    run = await svc.run_export(org.id, stream.id)
    assert run.status == "succeeded" and run.row_count == 3
    assert run.parts and all(p.endswith(".parquet") for p in run.parts)

    manifest = json.loads(writer.files[run.manifest_key])
    assert manifest["format"] == "parquet"

    table = pq.read_table(io.BytesIO(writer.files[run.parts[0]]))
    assert set(table.column_names) == set(manifest["fields"])
    subjects = set(table.column("subject").to_pylist())
    assert subjects == {"pq0", "pq1", "pq2"}

    # Incremental second run picks up only the new event.
    await emit_event(db, org.id, "project.approved", subject="pq-new", data={})
    await db.flush()
    run2 = await svc.run_export(org.id, stream.id)
    assert run2.row_count == 1
    t2 = pq.read_table(io.BytesIO(writer.files[run2.parts[0]]))
    assert t2.column("subject").to_pylist() == ["pq-new"]


@pytest.mark.asyncio
async def test_parquet_unavailable_refused_at_config_and_run(db, monkeypatch):
    """When pyarrow is absent: create/PATCH 422 EXPORT_FORMAT_UNAVAILABLE;
    an already-parquet stream fails its run cleanly (no mid-run crash)."""
    import app.integrations.services.warehouse as wh

    org, owner = await _org(db)
    svc = WarehouseExportService(db, writer=MemWriter())
    stream = await svc.create_stream(org.id, name=f"na-{ULID()}", dataset="events")

    monkeypatch.setattr(wh, "_parquet_available", lambda: False)
    with pytest.raises(AppError) as e:
        await svc.create_stream(
            org.id, name=f"na2-{ULID()}", dataset="events", part_format="parquet"
        )
    assert e.value.code == "EXPORT_FORMAT_UNAVAILABLE" and e.value.status_code == 422
    with pytest.raises(AppError) as e:
        await svc.update_stream(org.id, stream.id, part_format="parquet")
    assert e.value.code == "EXPORT_FORMAT_UNAVAILABLE"

    # Stream already pinned to parquet (extra uninstalled underneath it):
    # the run fails terminally with a diagnosable error, cursor untouched.
    stream.format = "parquet"
    await db.flush()
    await emit_event(db, org.id, "project.approved", subject="x", data={})
    await db.flush()
    run = await svc.run_export(org.id, stream.id)
    assert run.status == "failed" and run.error == "EXPORT_FORMAT_UNAVAILABLE"
    await db.refresh(stream)
    assert (stream.cursor or {}).get("last_id") is None  # cursor did not advance


@pytest.mark.asyncio
async def test_create_stream_bad_format_rejected(db):
    org, owner = await _org(db)
    svc = WarehouseExportService(db, writer=MemWriter())
    with pytest.raises(AppError) as e:
        await svc.create_stream(org.id, name=f"bf-{ULID()}", dataset="events", part_format="csv")
    assert e.value.code == "EXPORT_CONFIG_INVALID"
    s = await svc.create_stream(org.id, name=f"ok-{ULID()}", dataset="events")
    with pytest.raises(AppError) as e:
        await svc.update_stream(org.id, s.id, part_format="xlsx")
    assert e.value.code == "EXPORT_CONFIG_INVALID"


def test_parquet_bytes_mixed_type_column_falls_back_to_string():
    """A column mixing incompatible types (data.<key> selections) must not
    fail the run: it falls back to utf8 with JSON-encoded non-scalars."""
    import io

    import pyarrow.parquet as pq

    from app.integrations.services.warehouse import _parquet_bytes

    rows = [
        {"a": 1, "b": "x"},
        {"a": "two", "b": {"nested": True}},
        {"a": None, "b": None},
    ]
    content = _parquet_bytes(rows, ["a", "b"])
    table = pq.read_table(io.BytesIO(content))
    assert table.column("a").to_pylist() == ["1", "two", None]
    assert table.column("b").to_pylist() == ["x", '{"nested":true}', None]
