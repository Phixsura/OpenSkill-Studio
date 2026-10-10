"""P5 tests — mapping evaluator matrix + sync engine (cursors, checkpoints,
conflicts, tombstones, echo suppression, field policies, crash resume)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.models import StagedRecord, SyncRecordResult
from app.integrations.services.mapping import MappingService, apply_mapping, validate_document
from app.integrations.services.sync_engine import (
    SyncProfileService,
    execute_run,
    reap_stale_runs,
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
        email=f"sy-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Sy",
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


# ── mapping document validation ──


def test_validate_document_matrix():
    ok = {"fields": [{"target": "title", "path": "classTitle"}]}
    assert validate_document(ok) == []
    assert validate_document({}) != []
    assert validate_document({"fields": []}) != []
    assert any(
        "invalid JMESPath" in p
        for p in validate_document({"fields": [{"target": "x", "path": "a[["}]})
    )
    assert any(
        "unknown transform" in p
        for p in validate_document(
            {"fields": [{"target": "x", "path": "a", "transform": ["eval"]}]}
        )
    )
    assert any(
        "duplicate" in p
        for p in validate_document(
            {"fields": [{"target": "x", "path": "a"}, {"target": "x", "path": "b"}]}
        )
    )
    assert any(
        "unknown keys" in p
        for p in validate_document({"fields": [{"target": "x", "path": "a", "python": "1"}]})
    )


def test_apply_mapping_matrix():
    doc = {
        "fields": [
            {"target": "title", "path": "classTitle", "transform": ["trim"]},
            {"target": "code", "path": "course.courseCode", "default": "UNKNOWN"},
            {
                "target": "role",
                "path": "role",
                "enum_map": {"teacher": "instructor", "aide": "instructor"},
                "enum_default": "student",
            },
            {"target": "begin", "path": "beginDate", "transform": ["trim", "date_iso"]},
            {"target": "size", "path": "meta.size", "transform": ["to_int"]},
            {"target": "total", "path": "sum(items[].v)"},
        ]
    }
    mapped, errors = apply_mapping(
        doc,
        {
            "classTitle": "  AI 101  ",
            "role": "teacher",
            "beginDate": " 2026-09-01 ",
            "meta": {"size": "25"},
            "items": [{"v": 1}, {"v": 2.5}],
        },
    )
    assert errors == []
    assert mapped == {
        "title": "AI 101",
        "code": "UNKNOWN",
        "role": "instructor",
        "begin": "2026-09-01",
        "size": 25,
        "total": 3.5,
    }
    # enum default fires on unknown values
    m2, e2 = apply_mapping(doc, {"role": "weird"})
    assert m2["role"] == "student" and not [e for e in e2 if e["field"] == "role"]
    # enum WITHOUT default -> enum_unmapped error
    doc2 = {"fields": [{"target": "r", "path": "role", "enum_map": {"a": "b"}}]}
    _, e3 = apply_mapping(doc2, {"role": "zzz"})
    assert e3[0]["code"] == "enum_unmapped"
    # bad transforms surface, never crash
    _, e4 = apply_mapping(
        {"fields": [{"target": "n", "path": "x", "transform": ["to_int"]}]}, {"x": "abc"}
    )
    assert e4[0]["code"] == "transform_to_int"
    # non-finite floats are rejected at the boundary (R87)
    _, e5 = apply_mapping(
        {"fields": [{"target": "v", "path": "x"}]}, {"x": float("inf")}
    )
    assert e5[0]["code"] == "non_finite"
    # oversized string rejected
    _, e6 = apply_mapping(
        {"fields": [{"target": "s", "path": "x"}]}, {"x": "y" * 20_000}
    )
    assert e6[0]["code"] == "too_long"


# ── mapping profile CRUD ──


@pytest.mark.asyncio
async def test_mapping_profile_crud_and_version_bump(db):
    org, _ = await _org(db)
    svc = MappingService(db)
    doc = {"fields": [{"target": "title", "path": "classTitle"}]}
    p = await svc.create(
        org.id, name=f"m-{ULID()}", direction="inbound", model="roster.class", document=doc
    )
    assert p.version == 1
    with pytest.raises(AppError) as e:
        await svc.create(
            org.id, name=f"m2-{ULID()}", direction="inbound", model="nope.model", document=doc
        )
    assert e.value.code == "MAPPING_INVALID"
    with pytest.raises(AppError) as e2:
        await svc.create(
            org.id,
            name=f"m3-{ULID()}",
            direction="inbound",
            model="roster.class",
            document={"fields": [{"target": "x", "path": "a[["}]},
        )
    assert e2.value.code == "MAPPING_EXPRESSION_INVALID"
    p2 = await svc.update_document(
        org.id, p.id, {"fields": [{"target": "title", "path": "title"}]}
    )
    assert p2.version == 2
    preview = await svc.preview(org.id, p.id, [{"title": "A"}])
    assert preview[0]["mapped"] == {"title": "A"}
    # cross-tenant uniform 404
    other, _ = await _org(db)
    with pytest.raises(AppError) as e3:
        await svc.get(other.id, p.id)
    assert e3.value.status_code == 404


# ── sync engine ──


class FakeRosterConnector:
    key = "oneroster"
    capabilities = frozenset({"roster.read"})

    def __init__(self, batches, crash_after=None, respect_state=True):
        self.batches = batches
        self.crash_after = crash_after
        # A FRESH incremental source ignores a cursor minted by a previous
        # fake (state is provider-opaque); resume tests keep respect_state.
        self.respect_state = respect_state
        self.read_calls = []

    async def ping(self, ctx):
        return None

    async def read(self, ctx, model, state):
        self.read_calls.append(dict(state))
        # resume: skip batches already covered by the cursor
        start = int(state.get("batch", 0)) if self.respect_state else 0
        for i, batch in enumerate(self.batches[start:], start=start):
            if self.crash_after is not None and i >= self.crash_after:
                self.crash_after = None  # crash once, succeed on retry
                raise RuntimeError("connector crash")
            yield {"records": batch, "state": {"batch": i + 1}}


async def _setup_profile(db, org, owner, connector, field_policy=None, mapping=None):
    from app.integrations import registry
    from app.integrations.services.connections import ConnectionService

    csvc = ConnectionService(db)
    await csvc.sync_provider_catalog()
    await db.flush()
    conn = await csvc.create(
        org.id,
        provider_key="oneroster",
        name=f"c-{uuid.uuid4().hex[:8]}",
        config={"token_url": "https://idp.example.com/token"},
        base_url="https://sis.example.com/ims/oneroster",
        created_by=owner.id,
    )
    conn.status = "active"
    registry.CONNECTORS["oneroster"] = connector  # test connector
    mapping_id = None
    if mapping is not None:
        mp = await MappingService(db).create(
            org.id,
            name=f"map-{uuid.uuid4().hex[:6]}",
            direction="inbound",
            model="roster.class",
            document=mapping,
        )
        mapping_id = mp.id
    profile = await SyncProfileService(db).create(
        org.id,
        connection_id=conn.id,
        name=f"p-{uuid.uuid4().hex[:6]}",
        model="roster.class",
        direction="pull",
        mapping_profile_id=mapping_id,
        field_policy=field_policy or {},
    )
    await db.commit()
    return conn, profile


@pytest.mark.asyncio
async def test_capability_gate_blocks_wrong_provider(db):
    org, owner = await _org(db)
    from app.integrations.services.connections import ConnectionService

    csvc = ConnectionService(db)
    await csvc.sync_provider_catalog()
    conn = await csvc.create(
        org.id,
        provider_key="generic_rest",  # declares no roster.read
        name=f"c-{uuid.uuid4().hex[:8]}",
        config={},
        base_url="https://api.example.com/v1",
        created_by=owner.id,
    )
    with pytest.raises(AppError) as e:
        await SyncProfileService(db).create(
            org.id,
            connection_id=conn.id,
            name="p",
            model="roster.class",
            direction="pull",
            mapping_profile_id=None,
        )
    assert e.value.code == "CAPABILITY_MISSING"


@pytest.mark.asyncio
async def test_run_happy_path_counts_and_cursor(db):
    org, owner = await _org(db)
    fake = FakeRosterConnector(
        [
            [{"external_id": "c1", "title": "A"}, {"external_id": "c2", "title": "B"}],
            [{"external_id": "c3", "title": "C"}],
        ]
    )
    conn, profile = await _setup_profile(db, org, owner, fake)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    # idempotent second trigger returns the live run
    run2 = await SyncProfileService(db).trigger(org.id, profile.id)
    assert run2.id == run.id
    await db.commit()
    await execute_run(db, run.id)
    await db.refresh(run)
    assert run.status == "succeeded"
    assert run.stats["read"] == 3 and run.stats["created"] == 3
    assert run.cursor_out == {"batch": 2}
    staged = (
        await db.execute(
            select(StagedRecord).where(StagedRecord.connection_id == conn.id)
        )
    ).scalars().all()
    assert len(staged) == 3

    # Second incremental run with unchanged data: all unchanged, cursor resumes.
    fake2 = FakeRosterConnector([[{"external_id": "c1", "title": "A"}]], respect_state=False)
    from app.integrations import registry

    registry.CONNECTORS["oneroster"] = fake2
    runb = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, runb.id)
    await db.refresh(runb)
    assert runb.cursor_in == {"batch": 2}  # destination-confirmed state flows in
    assert runb.stats["unchanged"] == 1 and runb.status == "succeeded"
    # unchanged leaves NO record rows (§11.4 — counters only)
    rows = (
        await db.execute(select(SyncRecordResult).where(SyncRecordResult.run_id == runb.id))
    ).scalars().all()
    assert rows == []


@pytest.mark.asyncio
async def test_crash_resumes_from_committed_cursor_no_dupes(db):
    org, owner = await _org(db)
    fake = FakeRosterConnector(
        [
            [{"external_id": "r1", "v": "1"}],
            [{"external_id": "r2", "v": "2"}],
        ],
        crash_after=1,  # crash before batch 2 on the first attempt
    )
    conn, profile = await _setup_profile(db, org, owner, fake)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    await db.refresh(run)
    assert run.status == "failed"
    assert run.cursor_out == {"batch": 1}  # batch 1 committed before the crash

    # Retry: a NEW run starts from the last SUCCEEDED cursor ({} here since
    # the failed run never succeeded) — records are idempotent upserts, so
    # re-reading batch 1 creates no duplicates.
    run2 = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run2.id)
    await db.refresh(run2)
    assert run2.status == "succeeded"
    staged = (
        await db.execute(
            select(StagedRecord).where(StagedRecord.connection_id == conn.id)
        )
    ).scalars().all()
    assert sorted(s.external_id for s in staged) == ["r1", "r2"]
    # the re-read r1 counted as unchanged, not duplicate-created
    assert run2.stats["created"] == 1 and run2.stats["unchanged"] == 1


@pytest.mark.asyncio
async def test_mapping_conflicts_and_duplicate_ids(db):
    org, owner = await _org(db)
    mapping = {
        "fields": [
            {"target": "title", "path": "name"},
            {"target": "grade", "path": "grade", "enum_map": {"ten": "10"}},
        ]
    }
    fake = FakeRosterConnector(
        [
            [
                {"external_id": "k1", "name": "OK", "grade": "ten"},
                {"external_id": "k2", "name": "Bad", "grade": "eleven"},  # enum_unmapped
                {"external_id": "k1", "name": "Dup", "grade": "ten"},  # duplicate
            ]
        ]
    )
    conn, profile = await _setup_profile(db, org, owner, fake, mapping=mapping)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    await db.refresh(run)
    assert run.status == "partial"
    assert run.stats["created"] == 1 and run.stats["conflicts"] == 2
    results = await SyncProfileService(db).run_records(org.id, run.id, outcome="conflict")
    classes = {r.conflict_class for r in results}
    assert classes == {"enum_unmapped", "duplicate_external_id"}
    # mapped payload (not raw) is what got staged
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id, StagedRecord.external_id == "k1"
            )
        )
    ).scalar_one()
    assert staged.payload == {"title": "OK", "grade": "10"}


@pytest.mark.asyncio
async def test_tombstones_only_on_backfill(db):
    org, owner = await _org(db)
    fake = FakeRosterConnector([[{"external_id": "t1"}, {"external_id": "t2"}]])
    conn, profile = await _setup_profile(db, org, owner, fake)
    run = await SyncProfileService(db).trigger(org.id, profile.id, trigger="backfill")
    await db.commit()
    await execute_run(db, run.id)

    # Incremental delta missing t2: NOT a delete.
    from app.integrations import registry

    registry.CONNECTORS["oneroster"] = FakeRosterConnector([[{"external_id": "t1"}]], respect_state=False)
    run2 = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run2.id)
    t2 = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id, StagedRecord.external_id == "t2"
            )
        )
    ).scalar_one()
    assert t2.status == "active"

    # Backfill snapshot missing t2: tombstoned (never deleted).
    registry.CONNECTORS["oneroster"] = FakeRosterConnector([[{"external_id": "t1"}]], respect_state=False)
    run3 = await SyncProfileService(db).trigger(org.id, profile.id, trigger="backfill")
    await db.commit()
    await execute_run(db, run3.id)
    await db.refresh(t2)
    assert t2.status == "tombstoned"
    await db.refresh(run3)
    assert run3.stats["tombstoned"] == 1


@pytest.mark.asyncio
async def test_field_policy_ours_theirs_prefer_and_clock(db):
    org, owner = await _org(db)
    policy = {
        "owned": "ours",
        "shared": "theirs",
        "fill": "prefer_ours_unless_blank",
        "timed": "most_recent",
        "_default": "theirs",
    }
    fake = FakeRosterConnector(
        [[{"external_id": "f1", "owned": "A", "shared": "A", "fill": "A", "timed": "A"}]]
    )
    conn, profile = await _setup_profile(db, org, owner, fake, field_policy=policy)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)

    # Seed local state: we own "owned", fill has a value, timed has our ts.
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id, StagedRecord.external_id == "f1"
            )
        )
    ).scalar_one()
    staged.payload = {
        "owned": "LOCAL",
        "shared": "LOCAL",
        "fill": "LOCAL",
        "timed": "LOCAL",
        "_updated_at": "2026-10-10T00:00:00+00:00",
    }
    staged.raw_hash = "seeded"
    await db.commit()

    from app.integrations import registry

    registry.CONNECTORS["oneroster"] = FakeRosterConnector(
        respect_state=False,
        batches=[
            [
                {
                    "external_id": "f1",
                    "owned": "REMOTE",
                    "shared": "REMOTE",
                    "fill": "REMOTE",
                    "timed": "REMOTE",
                    "updated_at": "2026-10-11T00:00:00+00:00",  # newer than ours
                }
            ]
        ]
    )
    run2 = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run2.id)
    await db.refresh(staged)
    assert staged.payload["owned"] == "LOCAL"  # ours: inbound never overwrites
    assert staged.payload["shared"] == "REMOTE"  # theirs
    assert staged.payload["fill"] == "LOCAL"  # prefer_ours_unless_blank, not blank
    assert staged.payload["timed"] == "REMOTE"  # most_recent, theirs newer

    # most_recent with MISSING timestamps -> conflict row, field untouched.
    registry.CONNECTORS["oneroster"] = FakeRosterConnector(
        [[{"external_id": "f1", "timed": "NO-TS"}]], respect_state=False
    )
    staged.payload = dict(staged.payload)
    staged.payload.pop("_updated_at", None)
    staged.raw_hash = "seeded2"
    await db.commit()
    run3 = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run3.id)
    results = await SyncProfileService(db).run_records(org.id, run3.id, outcome="conflict")
    assert any(r.conflict_class == "clock_unresolvable" for r in results)
    await db.refresh(staged)
    assert staged.payload["timed"] == "REMOTE"  # unchanged by the conflicted run


@pytest.mark.asyncio
async def test_echo_suppression(db):
    org, owner = await _org(db)
    fake = FakeRosterConnector([[{"external_id": "e1", "v": "ours"}]])
    conn, profile = await _setup_profile(db, org, owner, fake)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id, StagedRecord.external_id == "e1"
            )
        )
    ).scalar_one()
    # Simulate our outbound write of {"v": "pushed"}.
    from app.integrations.services.sync_engine import _payload_hash

    # The engine hashes the FULL mapped payload (raw passthrough here, so
    # external_id is part of it) — the outbound writer must do the same.
    staged.last_outbound = {
        "fields_hash": _payload_hash({"external_id": "e1", "v": "pushed"}),
        "written_at": datetime.now(UTC).isoformat(),
    }
    await db.commit()
    # The provider reflects our own write back: must count as unchanged.
    from app.integrations import registry

    registry.CONNECTORS["oneroster"] = FakeRosterConnector([[{"external_id": "e1", "v": "pushed"}]], respect_state=False)
    run2 = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run2.id)
    await db.refresh(run2)
    assert run2.stats["unchanged"] == 1 and run2.stats.get("updated", 0) == 0


@pytest.mark.asyncio
async def test_reap_stale_runs(db):
    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    conn, profile = await _setup_profile(db, org, owner, fake)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    run.status = "running"
    run.heartbeat_at = datetime.now(UTC) - timedelta(minutes=30)
    await db.commit()
    reaped = await reap_stale_runs(db)
    await db.commit()
    assert reaped >= 1
    await db.refresh(run)
    assert run.status == "failed" and run.error["class"] == "stale_heartbeat"


@pytest.mark.asyncio
async def test_run_scoping_uniform_404(db):
    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    _, profile = await _setup_profile(db, org, owner, fake)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    other, _ = await _org(db)
    svc = SyncProfileService(db)
    for call in (
        lambda: svc.cancel(other.id, run.id),
        lambda: svc.run_records(other.id, run.id),
    ):
        with pytest.raises(AppError) as e:
            await call()
        assert e.value.status_code == 404


# ── R7 adversarial-review regression pins ──


def test_mapping_document_size_cap():
    from app.integrations.services.mapping import validate_document

    huge = {"fields": [{"target": "x", "path": "a", "default": "y" * 70_000}]}
    assert validate_document(huge) == ["document: exceeds 64KB"]


@pytest.mark.asyncio
async def test_disabled_provider_refuses_trigger(db):
    from app.integrations.models import IntegrationProvider

    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    conn, profile = await _setup_profile(db, org, owner, fake)
    provider = (
        await db.execute(
            select(IntegrationProvider).where(IntegrationProvider.key == "oneroster")
        )
    ).scalars().first()
    provider.enabled = False
    await db.flush()
    with pytest.raises(AppError) as e:
        await SyncProfileService(db).trigger(org.id, profile.id)
    assert e.value.code == "PROVIDER_DISABLED"
    provider.enabled = True  # restore for sibling tests
    await db.commit()


@pytest.mark.asyncio
async def test_trigger_reaps_stale_run_and_starts_fresh(db):
    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    conn, profile = await _setup_profile(db, org, owner, fake)
    svc = SyncProfileService(db)
    stuck = await svc.trigger(org.id, profile.id)
    stuck.status = "running"
    stuck.heartbeat_at = datetime.now(UTC) - timedelta(minutes=30)
    await db.commit()
    fresh = await svc.trigger(org.id, profile.id)
    assert fresh.id != stuck.id
    await db.refresh(stuck)
    assert stuck.status == "failed" and stuck.error["class"] == "stale_heartbeat"


# ── R11: scheduled-profile sweep (nothing else drives `schedule`) ──


@pytest.mark.asyncio
async def test_sweep_scheduled_profiles_triggers_due_only(db):
    from app.integrations.models import SyncRun
    from app.integrations.services.sync_engine import sweep_scheduled_profiles

    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    conn, profile = await _setup_profile(db, org, owner, fake)
    profile.schedule = "hourly"
    await db.commit()
    # No prior run -> due now.
    assert await sweep_scheduled_profiles(db) == 1
    run = (
        await db.execute(select(SyncRun).where(SyncRun.profile_id == profile.id))
    ).scalars().first()
    assert run is not None and run.trigger == "schedule"
    # A live run exists -> idempotent trigger returns it; sweep counts it but
    # creates no second run.
    await sweep_scheduled_profiles(db)
    runs = (
        await db.execute(select(SyncRun).where(SyncRun.profile_id == profile.id))
    ).scalars().all()
    assert len(runs) == 1
    # Finish the run recently -> NOT due within the hour.
    runs[0].status = "succeeded"
    await db.commit()
    assert await sweep_scheduled_profiles(db) == 0
