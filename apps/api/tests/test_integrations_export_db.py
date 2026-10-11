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


# ── R16: scheduled export sweep (same gap class as scheduled syncs) ──


@pytest.mark.asyncio
async def test_sweep_scheduled_exports_runs_due_daily_streams(db):
    from app.integrations.services.warehouse import sweep_scheduled_exports

    org, owner = await _org(db)
    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)
    daily = await svc.create_stream(
        org.id, name=f"d-{ULID()}", dataset="events", schedule="daily"
    )
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
        org.id, name=f"ha-{ULID()}", dataset="events",
        field_allowlist=["id", "subject"], anonymize={"subject": "hash"},
    )
    sb = await WarehouseExportService(db, writer=w2).create_stream(
        org2.id, name=f"hb-{ULID()}", dataset="events",
        field_allowlist=["id", "subject"], anonymize={"subject": "hash"},
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
        org.id, s.id,
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
            display_name="L", role=UserRole.STUDENT, status=UserStatus.ACTIVE,
        )
        db.add(learner)
        await db.flush()
        db.add(OrgMember(org_id=org.id, user_id=learner.id, role=OrgRole.STUDENT,
                         status=MemberStatus.ACTIVE))
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
            org.id, name=f"en-{ULID()}", dataset="enrollments",
            field_allowlist=["id", "cohort_id", "role"], anonymize={},
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
        db, org.id, "project.approved", subject="p1",
        data={"score": 97, "secret_note": "do not export", "learner": "u_1"},
    )
    await db.flush()
    writer = MemWriter()
    svc = WarehouseExportService(db, writer=writer)

    stream = await svc.create_stream(
        org.id, name=f"dk-{ULID()}", dataset="events",
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
            org.id, name=f"bad-{ULID()}", dataset="enrollments",
            field_allowlist=["id", "data.score"],
        )
    assert e2.value.code == "EXPORT_FIELD_NOT_ALLOWED"
    with pytest.raises(AppError) as e3:
        await svc.create_stream(
            org.id, name=f"bad-{ULID()}", dataset="events",
            field_allowlist=[f"data.k{i}" for i in range(21)],
        )
    assert e3.value.code == "EXPORT_CONFIG_INVALID"

    # update_stream enforces the same rules
    with pytest.raises(AppError):
        await svc.update_stream(org.id, stream.id, field_allowlist=["data"])
    updated = await svc.update_stream(
        org.id, stream.id, field_allowlist=["id", "data.score"]
    )
    assert updated.field_allowlist == ["id", "data.score"]
