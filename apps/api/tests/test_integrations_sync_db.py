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
    # R164: transform list is length-capped and type-guarded.
    assert any(
        "more than" in p
        for p in validate_document(
            {"fields": [{"target": "x", "path": "a", "transform": ["trim"] * 50}]}
        )
    )
    assert any(
        "must be a list" in p
        for p in validate_document(
            {"fields": [{"target": "x", "path": "a", "transform": "trim"}]}
        )
    )


def test_transforms_and_boundaries_matrix():
    """R26: mutation probe killed only 3/20 — these pin every transform's
    contract and every boundary constant in the evaluator."""
    from app.integrations.services.mapping import (
        MAX_INPUT_BYTES,
        MAX_RESULT_DEPTH,
        _t_coalesce_empty_null,
        _t_date_iso,
        _t_datetime_iso,
        _t_first,
        _t_split_csv,
        _t_to_decimal,
        _t_to_int,
        _t_to_string,
        _TransformError,
    )

    # to_string: booleans are JSON "true"/"false", never "True".
    assert _t_to_string(True) == "true" and _t_to_string(False) == "false"
    assert _t_to_string(None) is None and _t_to_string(5) == "5"
    # to_int: bools are NOT integers; float-strings are NOT integers;
    # the JS-safe bound is exactly 2**53 exclusive on both sides.
    for bad in (True, False, "4.5", "x"):
        with pytest.raises(_TransformError):
            _t_to_int(bad)
    assert _t_to_int(str(2**53 - 1)) == 2**53 - 1
    for edge in (2**53, -(2**53), 2**60, -(2**60)):
        with pytest.raises(_TransformError):
            _t_to_int(str(edge))
    assert _t_to_int("  7 ") == 7 and _t_to_int("") is None
    # to_decimal: non-finite rejected, finite normalized to string.
    for bad in ("NaN", "Infinity", "-Infinity"):
        with pytest.raises(_TransformError):
            _t_to_decimal(bad)
    assert _t_to_decimal("1.50") == "1.50" and _t_to_decimal(None) is None
    # date_iso: empty string -> None (not error); truncates to 10 chars so a
    # datetime input is accepted as its date part.
    assert _t_date_iso("") is None and _t_date_iso(None) is None
    assert _t_date_iso("2026-10-11T23:59:59") == "2026-10-11"
    with pytest.raises(_TransformError):
        _t_date_iso("2026-13-99")
    # datetime_iso: empty -> None; Z normalized.
    assert _t_datetime_iso("") is None
    assert _t_datetime_iso("2026-10-11T01:02:03Z") == "2026-10-11T01:02:03+00:00"
    # split_csv: blanks dropped, empty -> [], lists pass through.
    assert _t_split_csv("a, ,b,,c ") == ["a", "b", "c"]
    assert _t_split_csv("") == [] and _t_split_csv(None) == []
    assert _t_split_csv(["x"]) == ["x"]
    # first: FIRST element, never last; empty list -> None.
    assert _t_first(["a", "b"]) == "a" and _t_first([]) is None and _t_first("s") == "s"
    # coalesce_empty_null: ALL empty shapes collapse.
    assert _t_coalesce_empty_null("") is None
    assert _t_coalesce_empty_null([]) is None
    assert _t_coalesce_empty_null({}) is None
    assert _t_coalesce_empty_null(0) == 0

    doc = {"fields": [{"target": "x", "path": "a", "default": "D"}]}
    # default applies ONLY when the path yields None — a present value wins.
    assert apply_mapping(doc, {"a": "V"})[0] == {"x": "V"}
    assert apply_mapping(doc, {})[0] == {"x": "D"}
    # input cap is exclusive at MAX_INPUT_BYTES: a record AT the cap passes.
    pad = {"a": "V", "p": "y" * (MAX_INPUT_BYTES - len('{"a": "V", "p": ""}'))}
    assert len(__import__("json").dumps(pad)) == MAX_INPUT_BYTES
    mapped, errors = apply_mapping(doc, pad)
    assert errors == [] and mapped == {"x": "V"}
    # depth cap: a value of depth MAX_RESULT_DEPTH is refused, depth-1 passes.
    deep = ok_depth = "leaf"
    for _ in range(MAX_RESULT_DEPTH):
        deep = [deep]
    for _ in range(MAX_RESULT_DEPTH - 1):
        ok_depth = [ok_depth]
    assert apply_mapping(doc, {"a": deep})[1][0]["code"] == "too_deep"
    assert apply_mapping(doc, {"a": ok_depth})[1] == []
    # validate_document: target length bound is exactly 100.
    assert validate_document({"fields": [{"target": "t" * 100, "path": "a"}]}) == []
    assert validate_document({"fields": [{"target": "t" * 101, "path": "a"}]}) != []


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
async def test_conflict_resolution_accept_theirs_keep_ours(db):
    """R22: drives resolved_by/resolved_action — accept_theirs applies the
    stored source value to the staged record; double-resolve is 409;
    cross-org resolve is a uniform 404."""
    org, owner = await _org(db)
    policy = {"timed": "most_recent", "_default": "theirs"}
    fake = FakeRosterConnector([[{"external_id": "c1", "timed": "A"}]])
    conn, profile = await _setup_profile(db, org, owner, fake, field_policy=policy)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id, StagedRecord.external_id == "c1"
            )
        )
    ).scalar_one()
    staged.payload = {"timed": "LOCAL"}  # no _updated_at -> clock tie
    staged.raw_hash = "seeded"
    await db.commit()

    from app.integrations import registry

    registry.CONNECTORS["oneroster"] = FakeRosterConnector(
        [[{"external_id": "c1", "timed": "REMOTE"}]], respect_state=False
    )
    run2 = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run2.id)
    svc = SyncProfileService(db)
    conflicts = await svc.run_records(org.id, run2.id, outcome="conflict")
    row = next(r for r in conflicts if r.conflict_class == "clock_unresolvable")
    assert row.detail == {"field": "timed", "ours": "LOCAL", "theirs": "REMOTE"}

    # accept_theirs applies the source value and recomputes the hash.
    resolved = await svc.resolve_conflict(
        org.id, run2.id, row.id, action="accept_theirs", actor_id=owner.id
    )
    await db.commit()
    assert resolved.resolved_action == "accept_theirs" and resolved.resolved_by == owner.id
    await db.refresh(staged)
    assert staged.payload["timed"] == "REMOTE"

    # Double resolve -> 409.
    with pytest.raises(AppError) as exc:
        await svc.resolve_conflict(org.id, run2.id, row.id, action="dismiss", actor_id=owner.id)
    assert exc.value.status_code == 409

    # Cross-org: uniform 404 on the run.
    org2, _ = await _org(db)
    with pytest.raises(AppError) as exc2:
        await svc.resolve_conflict(org2.id, run2.id, row.id, action="dismiss", actor_id=owner.id)
    assert exc2.value.status_code == 404

    # keep_ours on a fresh conflict marks without touching staged data.
    staged.payload = {"timed": "LOCAL2"}
    staged.raw_hash = "seeded3"
    await db.commit()
    registry.CONNECTORS["oneroster"] = FakeRosterConnector(
        [[{"external_id": "c1", "timed": "REMOTE2"}]], respect_state=False
    )
    run3 = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run3.id)
    row3 = next(
        r
        for r in await svc.run_records(org.id, run3.id, outcome="conflict")
        if r.conflict_class == "clock_unresolvable"
    )
    await svc.resolve_conflict(org.id, run3.id, row3.id, action="keep_ours", actor_id=owner.id)
    await db.commit()
    await db.refresh(staged)
    assert staged.payload["timed"] == "LOCAL2"


@pytest.mark.asyncio
async def test_conflict_accept_theirs_refuses_stale(db):
    """R23: a later run moved the field -> accept_theirs is 409, data kept."""
    org, owner = await _org(db)
    policy = {"timed": "most_recent", "_default": "theirs"}
    fake = FakeRosterConnector([[{"external_id": "s1", "timed": "A"}]])
    conn, profile = await _setup_profile(db, org, owner, fake, field_policy=policy)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id, StagedRecord.external_id == "s1"
            )
        )
    ).scalar_one()
    staged.payload = {"timed": "LOCAL"}
    staged.raw_hash = "seeded"
    await db.commit()
    from app.integrations import registry

    registry.CONNECTORS["oneroster"] = FakeRosterConnector(
        [[{"external_id": "s1", "timed": "REMOTE"}]], respect_state=False
    )
    run2 = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run2.id)
    svc = SyncProfileService(db)
    row = next(
        r
        for r in await svc.run_records(org.id, run2.id, outcome="conflict")
        if r.conflict_class == "clock_unresolvable"
    )
    # Simulate a later run having moved the field.
    staged.payload = {"timed": "NEWER", "_updated_at": "2026-10-12T00:00:00+00:00"}
    staged.raw_hash = "moved"
    await db.commit()
    with pytest.raises(AppError) as exc:
        await svc.resolve_conflict(
            org.id, run2.id, row.id, action="accept_theirs", actor_id=owner.id
        )
    assert exc.value.status_code == 409
    await db.refresh(staged)
    assert staged.payload["timed"] == "NEWER"  # untouched
    # keep_ours still allowed on the stale row (mark-only is always safe).
    await svc.resolve_conflict(org.id, run2.id, row.id, action="keep_ours", actor_id=owner.id)


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
    # No prior run -> due now. Assert on OUR profile, not the global count —
    # the shared DB may hold hourly profiles from prior test runs that come
    # due again an hour later (time-dependent pollution).
    assert await sweep_scheduled_profiles(db) >= 1
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
    # Finish the run recently -> NOT due within the hour (profile-scoped).
    runs[0].status = "succeeded"
    await db.commit()
    await sweep_scheduled_profiles(db)
    runs_after = (
        await db.execute(select(SyncRun).where(SyncRun.profile_id == profile.id))
    ).scalars().all()
    assert len(runs_after) == 1


# ── R33: sync-engine execution-core killers ──


@pytest.mark.asyncio
async def test_backfill_resets_cursor_and_terminal_guards(db):
    """Kills: backfill-keeps-cursor, re-executing a terminal run, and
    executing a run someone else already claimed."""
    org, owner = await _org(db)
    fake = FakeRosterConnector([[{"external_id": "b1", "v": "1"}]])
    conn, profile = await _setup_profile(db, org, owner, fake)
    svc = SyncProfileService(db)
    run = await svc.trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    await db.refresh(run)
    assert run.status == "succeeded" and run.cursor_out == {"batch": 1}

    # Terminal guard: re-executing a succeeded run is a hard no-op.
    calls_before = len(fake.read_calls)
    await execute_run(db, run.id)
    assert len(fake.read_calls) == calls_before

    # Backfill: cursor_in must RESET to {} (full re-read), not resume.
    run_b = await svc.trigger(org.id, profile.id, trigger="backfill")
    await db.commit()
    assert run_b.cursor_in == {}
    await execute_run(db, run_b.id)
    assert fake.read_calls[-1] == {}  # connector saw a fresh state

    # Claim guard: a run already in 'running' (claimed elsewhere) is not
    # re-entered by a second executor.
    run_c = await svc.trigger(org.id, profile.id)
    await db.commit()
    run_c.status = "running"
    run_c.started_at = datetime.now(UTC)
    await db.commit()
    calls_before = len(fake.read_calls)
    await execute_run(db, run_c.id)
    assert len(fake.read_calls) == calls_before
    run_c.status = "cancelled"  # tidy
    await db.commit()

    # Cancel guard: a finished run can never be cancelled (409).
    with pytest.raises(AppError) as exc:
        await svc.cancel(org.id, run.id)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_requeued_run_resumes_from_own_cursor_out(db):
    """A redelivered/requeued run with committed progress resumes from its
    OWN cursor_out, not from cursor_in."""
    org, owner = await _org(db)
    fake = FakeRosterConnector(
        [[{"external_id": "q1", "v": "1"}], [{"external_id": "q2", "v": "2"}]],
        crash_after=1,
    )
    conn, profile = await _setup_profile(db, org, owner, fake)
    svc = SyncProfileService(db)
    run = await svc.trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    await db.refresh(run)
    assert run.status == "failed" and run.cursor_out == {"batch": 1}
    # Simulate outbox redelivery of the same run object.
    run.status = "queued"
    run.error = None
    await db.commit()
    await execute_run(db, run.id)
    # The resumed read started from the committed checkpoint...
    assert fake.read_calls[-1] == {"batch": 1}
    await db.refresh(run)
    assert run.status == "succeeded" and run.cursor_out == {"batch": 2}


@pytest.mark.asyncio
async def test_sync_run_drivable_through_outbox_handler(db):
    """R62: the outbox handler must run the sync on a DEDICATED session —
    the per-batch commits inside execute_run are incompatible with the
    handler SAVEPOINT. Drives the real handler via process_outbox_once."""
    import app.integrations.worker  # noqa: F401 — registers handlers
    from app.controlplane.worker import process_outbox_once
    from app.integrations.models import SyncRun

    org, owner = await _org(db)
    fake = FakeRosterConnector([[{"external_id": "ob-1", "v": "1"}]])
    conn, profile = await _setup_profile(db, org, owner, fake)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    run_id = run.id
    for _ in range(6):
        n = await process_outbox_once(db, topics=["intg.sync.run"])
        if n == 0:
            break
    row = await db.get(SyncRun, run_id)
    await db.refresh(row)
    assert row.status == "succeeded" and row.stats.get("created") == 1


@pytest.mark.asyncio
async def test_profile_update_and_mapping_repin(db):
    """R82: schedule/enabled/policy edits validated; repin_mapping is an
    EXPLICIT act that moves the pinned version; cross-org uniform 404."""
    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    conn, profile = await _setup_profile(
        db, org, owner, fake,
        mapping={"fields": [{"target": "title", "path": "title"}]},
    )
    svc = SyncProfileService(db)
    assert profile.mapping_version == 1

    out = await svc.update(
        org.id, profile.id, schedule="hourly", enabled=False,
        field_policy={"_default": "theirs"},
    )
    assert out.schedule == "hourly" and out.enabled is False
    assert out.field_policy == {"_default": "theirs"}

    # Mapping bumps to v2; the profile stays pinned at v1 until repin.
    mp = await MappingService(db).get(org.id, profile.mapping_profile_id)
    await MappingService(db).update_document(
        org.id, mp.id, {"fields": [{"target": "title", "path": "title2"}]}
    )
    await db.refresh(profile)
    assert profile.mapping_version == 1
    out2 = await svc.update(org.id, profile.id, repin_mapping=True)
    assert out2.mapping_version == 2

    with pytest.raises(AppError):
        await svc.update(org.id, profile.id, schedule="sometimes")
    org2, _ = await _org(db)
    with pytest.raises(AppError) as exc:
        await svc.update(org2.id, profile.id, enabled=True)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_guards_profile_busy_and_mapping_in_use(db):
    """R84: live run refuses profile delete; pinned mapping refuses mapping
    delete; both deletable once clear."""
    from app.integrations.api.sync import delete_mapping_profile, delete_sync_profile
    from app.models.user import User as _User

    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    conn, profile = await _setup_profile(
        db, org, owner, fake,
        mapping={"fields": [{"target": "title", "path": "title"}]},
    )
    mapping_id = profile.mapping_profile_id
    owner_user = await db.get(_User, owner.id)
    svc = SyncProfileService(db)
    run = await svc.trigger(org.id, profile.id)
    await db.commit()

    with pytest.raises(AppError) as e1:
        await delete_sync_profile(org.id, profile.id, db=db, user=owner_user)
    assert e1.value.code == "SYNC_PROFILE_BUSY"
    with pytest.raises(AppError) as e2:
        await delete_mapping_profile(org.id, mapping_id, db=db, user=owner_user)
    assert e2.value.code == "MAPPING_IN_USE"

    await svc.cancel(org.id, run.id)
    await db.commit()
    await delete_sync_profile(org.id, profile.id, db=db, user=owner_user)
    await delete_mapping_profile(org.id, mapping_id, db=db, user=owner_user)
    from app.integrations.models import MappingProfile, SyncProfile

    assert await db.get(SyncProfile, profile.id) is None
    assert await db.get(MappingProfile, mapping_id) is None


@pytest.mark.asyncio
async def test_strict_schema_gate_blocks_broken_mappings(db):
    """R99: with options.strict_schema, a mapped payload missing a required
    key becomes a schema_invalid conflict (never staged); compliant records
    stage normally; the gate stays off by default."""
    from app.integrations import registry

    org, owner = await _org(db)
    fake = FakeRosterConnector(
        [[{"external_id": "ok-1", "title": "Has Title"},
          {"external_id": "bad-1", "v": "no-title"}]]
    )
    conn, profile = await _setup_profile(db, org, owner, fake)
    profile.options = {"strict_schema": True}
    await db.commit()
    svc = SyncProfileService(db)
    run = await svc.trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    await db.refresh(run)
    assert run.stats["created"] == 1 and run.stats["conflicts"] == 1
    rows = await svc.run_records(org.id, run.id, outcome="conflict")
    assert rows[0].external_id == "bad-1"
    assert rows[0].conflict_class == "schema_invalid"
    assert rows[0].detail == {"missing": ["title"]}
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id,
                StagedRecord.external_id == "bad-1",
            )
        )
    ).scalar_one_or_none()
    assert staged is None  # junk never staged

    # Default (no flag): the same record stages fine.
    registry.CONNECTORS["oneroster"] = FakeRosterConnector(
        [[{"external_id": "bad-1", "v": "no-title"}]], respect_state=False
    )
    profile.options = {}
    await db.commit()
    run2 = await svc.trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run2.id)
    await db.refresh(run2)
    assert run2.stats["conflicts"] == 0 and run2.stats["created"] == 1


@pytest.mark.asyncio
async def test_admin_mutations_write_audit_rows(db):
    """R100 (Part O): mapping create/update and sync-profile create write
    the append-only audit trail with the acting user."""
    from sqlalchemy import select as _select

    from app.controlplane.models.audit import CommercialAuditEvent as AuditEvent
    from app.integrations.api.sync import create_mapping
    from app.models.user import User as _User

    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    conn, _profile = await _setup_profile(db, org, owner, fake)
    owner_user = await db.get(_User, owner.id)

    import app.integrations.api.sync as sync_api

    doc = {"fields": [{"target": "title", "path": "title"}]}
    body = sync_api.MappingCreateRequest(
        name=f"au-{uuid.uuid4().hex[:6]}", direction="inbound",
        model="roster.class", document=doc,
    )
    out = await create_mapping(org.id, body, db=db, user=owner_user)
    await db.commit()
    mp_id = out["data"].id

    rows = (
        await db.execute(
            _select(AuditEvent).where(
                AuditEvent.target_type == "mapping_profile",
                AuditEvent.target_id == mp_id,
            )
        )
    ).scalars().all()
    assert [r.action for r in rows] == ["intg.mapping.created"]
    assert rows[0].actor_user_id == owner.id
    assert rows[0].tenant_id == org.tenant_id  # scoped to the tenant
    assert rows[0].after == {"model": "roster.class", "version": 1}


@pytest.mark.asyncio
async def test_mapping_preview_parity_with_run_and_guards(db):
    """R123 (Part H): preview shares the exact evaluator with the engine —
    the preview of a sample equals what a real run stages for that record.
    Non-dict samples degrade safely; >20 samples is refused."""
    from app.exceptions import AppError
    from app.integrations import registry

    org, owner = await _org(db)
    doc = {
        "fields": [
            {"target": "title", "path": "title", "transform": ["trim"]},
            {"target": "code", "path": "code", "transform": ["upper"]},
            {"target": "term", "path": "termId", "default": "T0"},
        ]
    }
    sample = {"title": "  Math 101  ", "code": "m1"}
    fake = FakeRosterConnector([[dict(sample, external_id="p1")]])
    conn, profile = await _setup_profile(db, org, owner, fake, mapping=doc)
    svc = MappingService(db)

    prev = await svc.preview(org.id, profile.mapping_profile_id, [sample])
    assert prev[0]["mapped"] == {"title": "Math 101", "code": "M1", "term": "T0"}
    assert prev[0]["errors"] == []

    # Real run stages the SAME mapped payload (parity).
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id, StagedRecord.external_id == "p1"
            )
        )
    ).scalar_one()
    for k, v in prev[0]["mapped"].items():
        assert staged.payload[k] == v

    # Non-dict sample -> empty mapped, no crash.
    prev2 = await svc.preview(org.id, profile.mapping_profile_id, ["not-a-dict"])
    # No crash; no real values leak from a non-dict (only the default fires).
    assert prev2[0]["mapped"].get("term") == "T0"
    assert prev2[0]["mapped"].get("code") is None

    # >20 samples refused.
    with pytest.raises(AppError) as exc:
        await svc.preview(org.id, profile.mapping_profile_id, [sample] * 21)
    assert exc.value.code == "MAPPING_PREVIEW_TOO_LARGE"
    assert registry is not None


@pytest.mark.asyncio
async def test_bidirectional_profile_rejected(db):
    """R124: bidirectional has no coherent single-profile execution (pull and
    push are different models) — creation must refuse it, not silently
    pull-only."""
    from app.exceptions import AppError

    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    conn, _p = await _setup_profile(db, org, owner, fake)
    with pytest.raises(AppError) as exc:
        await SyncProfileService(db).create(
            org.id, connection_id=conn.id, name=f"bi-{uuid.uuid4().hex[:6]}",
            model="roster.class", direction="bidirectional", mapping_profile_id=None,
        )
    assert exc.value.code == "SYNC_PROFILE_INVALID"
    assert "bidirectional" in exc.value.message


@pytest.mark.asyncio
async def test_connection_delete_refuses_while_run_live(db):
    """R174: deleting a connection cascade-deletes its sync profiles + runs;
    a live run must block the delete (CONNECTION_BUSY 409) so the worker is
    never left operating on a row ripped out from under it. Once the run
    reaches a terminal state the delete proceeds."""
    from app.exceptions import AppError
    from app.integrations.models import SyncRun
    from app.integrations.services.connections import ConnectionService

    org, owner = await _org(db)
    conn, profile = await _setup_profile(db, org, owner, FakeRosterConnector([[]]))

    # A QUEUED run (not yet picked up) must also block — a worker could claim
    # it the instant after the delete check.
    queued = SyncRun(profile_id=profile.id, status="queued", trigger="manual", cursor_in={})
    db.add(queued)
    await db.flush()
    with pytest.raises(AppError) as eq:
        await ConnectionService(db).delete(org.id, conn.id)
    assert eq.value.code == "CONNECTION_BUSY"
    queued.status = "cancelled"
    await db.flush()

    run = SyncRun(profile_id=profile.id, status="running", trigger="manual", cursor_in={})
    db.add(run)
    await db.flush()

    with pytest.raises(AppError) as e:
        await ConnectionService(db).delete(org.id, conn.id)
    assert e.value.code == "CONNECTION_BUSY" and e.value.status_code == 409

    run.status = "succeeded"
    await db.flush()
    run_id = run.id
    await ConnectionService(db).delete(org.id, conn.id)  # now allowed
    from sqlalchemy import func as _func
    n = (
        await db.execute(
            select(_func.count()).select_from(SyncRun).where(SyncRun.id == run_id)
        )
    ).scalar_one()
    assert n == 0  # cascade cleaned the run


@pytest.mark.asyncio
async def test_clock_conflict_tolerates_naive_provider_timestamp(db):
    """R179: a provider sending a NAIVE updated_at (no Z/offset) while our
    stored _updated_at is aware must NOT 500 the sync run via a naive-vs-
    aware comparison — most_recent still resolves (naive treated as UTC)."""
    org, owner = await _org(db)
    policy = {"timed": "most_recent", "_default": "theirs"}
    fake = FakeRosterConnector([[{"external_id": "n1", "timed": "A"}]])
    conn, profile = await _setup_profile(db, org, owner, fake, field_policy=policy)
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)

    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id, StagedRecord.external_id == "n1"
            )
        )
    ).scalar_one()
    staged.payload = {"timed": "LOCAL", "_updated_at": "2026-10-10T00:00:00+00:00"}
    staged.raw_hash = "seeded"
    await db.commit()

    from app.integrations import registry

    registry.CONNECTORS["oneroster"] = FakeRosterConnector(
        respect_state=False,
        batches=[[
            {
                "external_id": "n1", "timed": "REMOTE",
                "updated_at": "2026-10-11T00:00:00",  # NAIVE, newer than ours
            }
        ]],
    )
    run2 = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run2.id)  # must not raise
    await db.refresh(staged)
    assert staged.payload["timed"] == "REMOTE"  # naive treated as UTC, theirs newer


@pytest.mark.asyncio
async def test_sync_run_loads_connection_credentials(db):
    """R194: a sync run must decrypt the connection's stored credentials and
    hand them to the connector via ctx.get_secret() — otherwise real
    connectors (OneRoster OAuth, CRM api_key, ATS) authenticate with an empty
    secret and silently 401 while ping looks healthy."""
    from app.integrations import registry
    from app.integrations.services.connections import ConnectionService

    org, owner = await _org(db)

    seen_secret = {}

    class SecretCapturingConnector:
        key = "oneroster"
        capabilities = frozenset({"roster.read"})

        async def ping(self, ctx):
            return None

        async def read(self, ctx, model, state):
            seen_secret.update(await ctx.get_secret())
            yield {"records": [{"external_id": "s1", "title": "T"}], "state": {}}

    csvc = ConnectionService(db)
    await csvc.sync_provider_catalog()
    await db.flush()
    conn = await csvc.create(
        org.id, provider_key="oneroster", name=f"c-{uuid.uuid4().hex[:8]}",
        config={"token_url": "https://idp.example.com/token"},
        base_url="https://sis.example.com/ims/oneroster", created_by=owner.id,
    )
    conn.status = "active"
    await csvc.set_credential(
        org.id, conn.id, kind="client_secret",
        values={"client_id": "cid-123", "client_secret": "shhh-secret"},
        expires_at=None,
    )
    await db.flush()
    registry.CONNECTORS["oneroster"] = SecretCapturingConnector()

    profile = await SyncProfileService(db).create(
        org.id, connection_id=conn.id, name=f"p-{uuid.uuid4().hex[:6]}",
        model="roster.class", direction="pull", mapping_profile_id=None,
    )
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()
    await execute_run(db, run.id)

    assert seen_secret.get("client_secret") == "shhh-secret"
    assert seen_secret.get("client_id") == "cid-123"


@pytest.mark.asyncio
async def test_sync_preview_pull_dry_run(db):
    """R196: sync preview reads the first few records from the connector and
    shows mapped output, with NO staging, cursor advance, or run row."""
    from sqlalchemy import func as _func

    from app.integrations.models import StagedRecord, SyncRun

    org, owner = await _org(db)
    fake = FakeRosterConnector(
        [[{"external_id": "pv1", "title": "Algebra"}, {"external_id": "pv2", "title": "Calc"}]]
    )
    conn, profile = await _setup_profile(
        db, org, owner, fake,
        mapping={"fields": [{"target": "title", "path": "title", "transform": ["upper"]}]},
    )

    out = await SyncProfileService(db).preview(org.id, profile.id, limit=5)
    assert out["model"] == "roster.class"
    assert out["count"] == 2

    # limit is enforced ACROSS batches: with two batches of 3 and limit 3,
    # the preview must stop after the first batch — not spill into batch 2.
    big = FakeRosterConnector(
        [
            [{"external_id": f"a{i}", "title": "T"} for i in range(3)],
            [{"external_id": f"b{i}", "title": "T"} for i in range(3)],
        ]
    )
    from app.integrations import registry as _reg

    _reg.CONNECTORS["oneroster"] = big
    capped = await SyncProfileService(db).preview(org.id, profile.id, limit=3)
    assert capped["count"] == 3  # not 4+ (outer per-batch break enforces it)
    assert out["records"][0]["raw"]["external_id"] == "pv1"
    assert out["records"][0]["mapped"]["title"] == "ALGEBRA"  # transform applied
    assert out["records"][0]["errors"] == []

    # No side effects: no staged records, no run rows for this profile.
    staged = (
        await db.execute(
            _func.count(StagedRecord.id).select().where(
                StagedRecord.connection_id == conn.id
            )
        )
    ).scalar()
    assert staged in (0, None)
    runs = (
        await db.execute(
            select(_func.count(SyncRun.id)).where(SyncRun.profile_id == profile.id)
        )
    ).scalar_one()
    assert runs == 0


@pytest.mark.asyncio
async def test_sync_preview_rejects_push_profile(db):
    """R196: preview is pull-only — a push profile is a clean 422."""
    from app.exceptions import AppError

    org, owner = await _org(db)
    fake = FakeRosterConnector([[]])
    conn, profile = await _setup_profile(db, org, owner, fake)
    # Flip to push direction directly (create rejects bidirectional, not push).
    profile.direction = "push"
    await db.flush()
    with pytest.raises(AppError) as e:
        await SyncProfileService(db).preview(org.id, profile.id)
    assert e.value.code == "SYNC_PREVIEW_UNSUPPORTED"


@pytest.mark.asyncio
async def test_overfull_connector_page_fully_staged_never_mistombstoned(db, monkeypatch):
    """R215: a connector page larger than the engine's per-txn chunk must be
    staged COMPLETELY. The old `[: BATCH_SIZE * 2]` cap silently dropped the
    tail while advancing the cursor past it (permanent loss) — and a backfill
    then TOMBSTONED the dropped records (absent from the seen-set)."""
    from app.integrations.services import sync_engine as se

    monkeypatch.setattr(se, "BATCH_SIZE", 3)  # chunk=3; old cap would be 6
    org, owner = await _org(db)
    page = [
        {"sourcedId": f"of-{i}", "title": f"Class {i}", "status": "active"}
        for i in range(8)  # one page of 8 > old cap of 6
    ]
    conn, profile = await _setup_profile(db, org, owner, FakeRosterConnector([page]))
    run = await SyncProfileService(db).trigger(org.id, profile.id, trigger="backfill")
    await db.commit()
    await se.execute_run(db, run.id)

    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id,
                StagedRecord.model == "roster.class",
            )
        )
    ).scalars().all()
    assert len(staged) == 8
    assert all(s.status == "active" for s in staged)  # none mis-tombstoned
    refetched = await db.get(type(run), run.id)
    assert refetched.status == "succeeded"
    assert refetched.stats["created"] == 8 and refetched.stats["tombstoned"] == 0


@pytest.mark.asyncio
async def test_staged_lookup_batched_not_per_record(db, monkeypatch):
    """R218: the engine must prefetch each chunk's staged rows in ONE query —
    not a point SELECT per record (N+1: 500 round-trips per batch at
    enterprise volume). Counted at the cursor: 12 records in chunks of 3 must
    issue at most 6 staged-table SELECTs (4 chunk prefetches + tombstone pass
    + slack); the per-record version issues 13+."""
    from sqlalchemy import event

    from app.core.database import engine
    from app.integrations.services import sync_engine as se

    monkeypatch.setattr(se, "BATCH_SIZE", 3)
    org, owner = await _org(db)
    pages = [
        [{"sourcedId": f"nq-{p}-{i}", "title": f"C{p}{i}", "status": "active"}
         for i in range(6)]
        for p in range(2)
    ]
    conn, profile = await _setup_profile(db, org, owner, FakeRosterConnector(pages))
    run = await SyncProfileService(db).trigger(org.id, profile.id, trigger="backfill")
    await db.commit()

    counts = {"staged_selects": 0}

    def _count(conn_, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT") and "intg_staged_records" in statement:
            counts["staged_selects"] += 1

    sync_engine_ = engine.sync_engine
    event.listen(sync_engine_, "before_cursor_execute", _count)
    try:
        await se.execute_run(db, run.id)
    finally:
        event.remove(sync_engine_, "before_cursor_execute", _count)

    refetched = (
        await db.execute(select(type(run)).where(type(run).id == run.id))
    ).scalar_one()
    assert refetched.status == "succeeded" and refetched.stats["created"] == 12
    assert counts["staged_selects"] <= 6, counts


def test_mapping_rejects_overlong_path_expression():
    """R239 (mutation survivor pin): a single JMESPath longer than
    MAX_EXPR_LEN must be rejected at save — the 64KB document cap only
    partially shadows this (a many-KB single expression still compiles,
    and compile cost must stay bounded per field)."""
    doc = {"fields": [{"target": "x", "path": "a" + ("." + "b" * 60) * 20}]}
    assert len(doc["fields"][0]["path"]) > 500
    problems = validate_document(doc)
    assert any("path: required string <= 500" in p for p in problems), problems


@pytest.mark.asyncio
async def test_scheduled_sweep_never_triggers_manual_profiles(db):
    """R243 (survivor pin): a `manual` sync profile must never be triggered
    by the scheduled sweep — the documented R11 rule had no negative test."""
    from app.integrations.models import SyncRun
    from app.integrations.services.sync_engine import sweep_scheduled_profiles

    org, owner = await _org(db)
    _conn, profile = await _setup_profile(db, org, owner, FakeRosterConnector([[]]))
    assert profile.schedule == "manual"
    await db.commit()
    await sweep_scheduled_profiles(db)
    runs = (
        await db.execute(select(SyncRun).where(SyncRun.profile_id == profile.id))
    ).scalars().all()
    assert runs == []


def test_to_int_rejects_bool():
    """R248 (survivor pin): bool is an int subclass — to_int(True) silently
    becoming 1 corrupts typed fields. Must raise."""
    from app.integrations.services.mapping import apply_mapping

    doc = {"fields": [{"target": "n", "path": "v", "transform": ["to_int"]}]}
    mapped, errors = apply_mapping(doc, {"v": True})
    assert mapped == {} and errors and errors[0]["code"] == "transform_to_int"


@pytest.mark.asyncio
async def test_conflict_resolve_requires_result_belongs_to_run(db):
    """R250 (survivor pin, IDOR class): resolve must verify the result row
    BELONGS to the addressed run — dropping that check let a valid own-run id
    resolve a FOREIGN org's conflict row (the run is org-gated, the result
    was fetched by id alone)."""
    from app.integrations.models import SyncRecordResult

    org_a, owner_a = await _org(db)
    org_b, owner_b = await _org(db)
    # org B: a run with a conflict row.
    _conn_b, prof_b = await _setup_profile(db, org_b, owner_b, FakeRosterConnector([[]]))
    run_b = await SyncProfileService(db).trigger(org_b.id, prof_b.id)
    conflict_b = SyncRecordResult(
        run_id=run_b.id, external_id="x-1", model="roster.class",
        outcome="conflict", conflict_class="clock_unresolvable",
        detail={"field": "title", "ours": "a", "theirs": "b"},
    )
    db.add(conflict_b)
    # org A: its own run.
    _conn_a, prof_a = await _setup_profile(db, org_a, owner_a, FakeRosterConnector([[]]))
    run_a = await SyncProfileService(db).trigger(org_a.id, prof_a.id)
    await db.flush()

    with pytest.raises(AppError) as e:
        await SyncProfileService(db).resolve_conflict(
            org_a.id, run_a.id, conflict_b.id, action="dismiss", actor_id=owner_a.id
        )
    assert e.value.status_code == 404  # uniform 404, never resolved
    await db.refresh(conflict_b)
    assert conflict_b.resolved_action is None
