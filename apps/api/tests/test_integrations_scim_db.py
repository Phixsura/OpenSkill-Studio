"""P4 SCIM DB tests — provisioning lifecycle, Entra-quirk PATCH table,
deprovision session sweep, group deltas + mapping effects, filters, auth."""

import uuid
from datetime import UTC, datetime
from hashlib import sha256

import pytest
import pytest_asyncio
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.services.scim import (
    ScimError,
    ScimGroupService,
    ScimTokenService,
    ScimUserService,
)
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import RefreshToken, User, UserRole, UserStatus


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, email=None):
    u = User(
        email=email or f"scim-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Scim",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, user):
    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    tenant = await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )
    org = Organization(
        name=f"Org {ULID()}",
        slug=f"org-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    db.add(
        OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE)
    )
    await db.flush()
    return org


@pytest_asyncio.fixture
async def ctx(db):
    owner = await _user(db)
    org = await _org(db, owner)
    token, raw = await ScimTokenService(db).create(
        org.id, name="idp", group_map={}, created_by=owner.id
    )
    return {"db": db, "owner": owner, "org": org, "token": token, "raw": raw}


def _usvc(ctx) -> ScimUserService:
    return ScimUserService(ctx["db"], ctx["token"])


def _gsvc(ctx) -> ScimGroupService:
    return ScimGroupService(ctx["db"], ctx["token"])


# ── token auth ──


@pytest.mark.asyncio
async def test_token_auth_and_revocation(ctx):
    db = ctx["db"]
    svc = ScimTokenService(db)
    token = await svc.authenticate(ctx["raw"])
    assert token.id == ctx["token"].id and token.last_used_at is not None
    with pytest.raises(ScimError):
        await svc.authenticate("osks_scim_wrong")
    with pytest.raises(ScimError):
        await svc.authenticate("Bearer-garbage")
    await svc.revoke(ctx["org"].id, token.id)
    with pytest.raises(ScimError):
        await svc.authenticate(ctx["raw"])
    # raw token never stored
    assert ctx["token"].token_hash == sha256(ctx["raw"].encode()).hexdigest()


@pytest.mark.asyncio
async def test_token_group_map_validation_and_limit(ctx):
    db, org, owner = ctx["db"], ctx["org"], ctx["owner"]
    svc = ScimTokenService(db)
    with pytest.raises(AppError) as e:
        await svc.create(
            org.id,
            name="bad",
            group_map={"G": {"kind": "role", "role": "owner"}},
            created_by=owner.id,
        )
    assert e.value.code == "SCIM_GROUP_MAP_INVALID"
    for i in range(4):  # 1 exists from fixture
        await svc.create(org.id, name=f"t{i}", group_map={}, created_by=owner.id)
    with pytest.raises(AppError) as e2:
        await svc.create(org.id, name="t5", group_map={}, created_by=owner.id)
    assert e2.value.code == "SCIM_TOKEN_LIMIT"


# ── user lifecycle ──


@pytest.mark.asyncio
async def test_create_get_filter_roundtrip(ctx):
    email = f"u-{uuid.uuid4().hex[:8]}@corp.example.edu"
    res, _ = await _usvc(ctx).create(
        {"userName": email, "displayName": "U One", "externalId": "ext-1", "active": True}
    )
    assert res["userName"] == email and res["active"] is True
    assert res["externalId"] == "ext-1"
    got = await _usvc(ctx).get(res["id"])
    assert got["id"] == res["id"]
    # filters
    lst = await _usvc(ctx).list(filter_expr=f'userName eq "{email}"', start_index=1, count=100)
    assert lst["totalResults"] == 1 and lst["Resources"][0]["id"] == res["id"]
    lst2 = await _usvc(ctx).list(filter_expr='externalId eq "ext-1"', start_index=1, count=100)
    assert lst2["totalResults"] == 1
    lst3 = await _usvc(ctx).list(filter_expr='userName eq "nobody@x.y"', start_index=1, count=100)
    assert lst3["totalResults"] == 0 and lst3["Resources"] == []  # envelope even when empty
    with pytest.raises(ScimError):
        await _usvc(ctx).list(filter_expr="title pr", start_index=1, count=100)


@pytest.mark.asyncio
async def test_duplicate_409_and_reactivation(ctx):
    email = f"dup-{uuid.uuid4().hex[:8]}@corp.example.edu"
    res, _ = await _usvc(ctx).create({"userName": email})
    with pytest.raises(ScimError) as e:
        await _usvc(ctx).create({"userName": email})
    assert e.value.status == 409 and e.value.scim_type == "uniqueness"
    # Soft-delete then re-POST: reactivates, no 409 (draft-ansari rule).
    await _usvc(ctx).delete(res["id"])
    res2, _ = await _usvc(ctx).create({"userName": email})
    assert res2["id"] == res["id"] and res2["active"] is True


@pytest.mark.asyncio
async def test_membership_only_provision_for_existing_platform_user(ctx):
    db = ctx["db"]
    existing = await _user(db, email=f"cross-{uuid.uuid4().hex[:8]}@other.example.com")
    old_hash = existing.password_hash
    res, _ = await _usvc(ctx).create({"userName": existing.email})
    assert res["id"] == existing.id
    assert existing.password_hash == old_hash  # credentials untouched
    member = (
        await db.execute(
            select(OrgMember).where(
                OrgMember.org_id == ctx["org"].id, OrgMember.user_id == existing.id
            )
        )
    ).scalar_one()
    assert member.role == OrgRole.STUDENT


ENTRA_DEACTIVATION_PATCHES = [
    # canonical boolean
    {"Operations": [{"op": "replace", "path": "active", "value": False}]},
    # capital-R op + quoted string value
    {"Operations": [{"op": "Replace", "path": "active", "value": "False"}]},
    # lowercase quoted string
    {"Operations": [{"op": "replace", "path": "active", "value": "false"}]},
    # fully-qualified URN path
    {
        "Operations": [
            {
                "op": "replace",
                "path": "urn:ietf:params:scim:schemas:core:2.0:User:active",
                "value": False,
            }
        ]
    },
    # no path, value object
    {"Operations": [{"op": "replace", "value": {"active": False}}]},
]


@pytest.mark.asyncio
@pytest.mark.parametrize("patch_body", ENTRA_DEACTIVATION_PATCHES)
async def test_patch_deactivation_leniency_and_session_sweep(ctx, patch_body):
    db = ctx["db"]
    email = f"deact-{uuid.uuid4().hex[:8]}@corp.example.edu"
    res, _ = await _usvc(ctx).create({"userName": email})
    # Give the user a live refresh token — deprovision must revoke it.
    rt = RefreshToken(
        user_id=res["id"],
        token_hash=sha256(b"jti-test").hexdigest(),
        expires_at=datetime(2030, 1, 1, tzinfo=UTC),
    )
    db.add(rt)
    await db.flush()
    out = await _usvc(ctx).patch(res["id"], patch_body)
    assert out["active"] is False
    member = (
        await db.execute(
            select(OrgMember).where(
                OrgMember.org_id == ctx["org"].id, OrgMember.user_id == res["id"]
            )
        )
    ).scalar_one()
    assert member.status == MemberStatus.ARCHIVED
    await db.refresh(rt)
    assert rt.revoked_at is not None  # session sweep ran


@pytest.mark.asyncio
async def test_patch_invalid_op_rejects_whole_request(ctx):
    email = f"atom-{uuid.uuid4().hex[:8]}@corp.example.edu"
    res, _ = await _usvc(ctx).create({"userName": email, "displayName": "Before"})
    with pytest.raises(ScimError) as e:
        await _usvc(ctx).patch(
            res["id"],
            {
                "Operations": [
                    {"op": "replace", "path": "displayName", "value": "After"},
                    {"op": "explode", "path": "x", "value": 1},
                ]
            },
        )
    assert e.value.scim_type == "invalidSyntax"
    # First op must NOT have applied (validate-all-before-apply).
    got = await _usvc(ctx).get(res["id"])
    assert got["displayName"] == "Before"


@pytest.mark.asyncio
async def test_delete_equals_deactivate_and_cross_org_404(ctx):
    db = ctx["db"]
    email = f"del-{uuid.uuid4().hex[:8]}@corp.example.edu"
    res, _ = await _usvc(ctx).create({"userName": email})
    await _usvc(ctx).delete(res["id"])
    got = await _usvc(ctx).get(res["id"])
    assert got["active"] is False  # record retained, deactivated
    # A user in ANOTHER org is a 404 for this token (no oracle).
    outsider = await _user(db)
    other_org = await _org(db, outsider)
    other_token, _ = await ScimTokenService(db).create(
        other_org.id, name="other", group_map={}, created_by=outsider.id
    )
    with pytest.raises(ScimError) as e:
        await ScimUserService(db, other_token).get(res["id"])
    assert e.value.status == 404


# ── groups ──


@pytest.mark.asyncio
async def test_group_crud_and_member_deltas(ctx):
    email1 = f"g1-{uuid.uuid4().hex[:8]}@corp.example.edu"
    email2 = f"g2-{uuid.uuid4().hex[:8]}@corp.example.edu"
    u1, _ = await _usvc(ctx).create({"userName": email1})
    u2, _ = await _usvc(ctx).create({"userName": email2})
    g = await _gsvc(ctx).create({"displayName": "Engineering", "members": [{"value": u1["id"]}]})
    assert [m["value"] for m in g["members"]] == [u1["id"]]
    # delta add + filtered remove
    g2 = await _gsvc(ctx).patch(
        g["id"],
        {"Operations": [{"op": "add", "path": "members", "value": [{"value": u2["id"]}]}]},
    )
    assert len(g2["members"]) == 2
    g3 = await _gsvc(ctx).patch(
        g["id"],
        {"Operations": [{"op": "remove", "path": f'members[value eq "{u1["id"]}"]'}]},
    )
    assert [m["value"] for m in g3["members"]] == [u2["id"]]
    # replace computes the delta against current membership
    g4 = await _gsvc(ctx).patch(
        g["id"],
        {"Operations": [{"op": "replace", "path": "members", "value": [{"value": u1["id"]}]}]},
    )
    assert [m["value"] for m in g4["members"]] == [u1["id"]]
    # duplicate group name 409; unknown member 400
    with pytest.raises(ScimError) as e:
        await _gsvc(ctx).create({"displayName": "Engineering"})
    assert e.value.status == 409
    with pytest.raises(ScimError) as e2:
        await _gsvc(ctx).patch(
            g["id"],
            {"Operations": [{"op": "add", "path": "members", "value": [{"value": "01FAKE"}]}]},
        )
    assert e2.value.status == 400


@pytest.mark.asyncio
async def test_group_role_mapping_with_ceiling_and_revert(ctx):
    db = ctx["db"]
    ctx["token"].group_map = {"Instructors": {"kind": "role", "role": "instructor"}}
    await db.flush()
    email = f"rm-{uuid.uuid4().hex[:8]}@corp.example.edu"
    u, _ = await _usvc(ctx).create({"userName": email})
    g = await _gsvc(ctx).create({"displayName": "Instructors"})
    await _gsvc(ctx).patch(
        g["id"], {"Operations": [{"op": "add", "path": "members", "value": [{"value": u["id"]}]}]}
    )
    member = (
        await db.execute(
            select(OrgMember).where(OrgMember.org_id == ctx["org"].id, OrgMember.user_id == u["id"])
        )
    ).scalar_one()
    assert member.role == OrgRole.INSTRUCTOR
    # leaving the group reverts to student
    await _gsvc(ctx).patch(
        g["id"],
        {"Operations": [{"op": "remove", "path": f'members[value eq "{u["id"]}"]'}]},
    )
    assert member.role == OrgRole.STUDENT
    # an OWNER joining a mapped group is never demoted/promoted by sync
    owner_member = (
        await db.execute(
            select(OrgMember).where(
                OrgMember.org_id == ctx["org"].id, OrgMember.user_id == ctx["owner"].id
            )
        )
    ).scalar_one()
    await _gsvc(ctx).patch(
        g["id"],
        {"Operations": [{"op": "add", "path": "members", "value": [{"value": ctx["owner"].id}]}]},
    )
    assert owner_member.role == OrgRole.OWNER


@pytest.mark.asyncio
async def test_group_cohort_mapping(ctx):
    db = ctx["db"]
    from app.services.cohort import CohortService

    cohort = await CohortService(db).create_cohort(
        org_id=ctx["org"].id, name=f"C {ULID()}", description=None, created_by=ctx["owner"].id
    )
    ctx["token"].group_map = {"Class A": {"kind": "cohort", "id": cohort.id}}
    await db.flush()
    email = f"cm-{uuid.uuid4().hex[:8]}@corp.example.edu"
    u, _ = await _usvc(ctx).create({"userName": email})
    g = await _gsvc(ctx).create({"displayName": "Class A", "members": [{"value": u["id"]}]})
    from app.models.cohort import CohortMember

    cm = (
        await db.execute(
            select(CohortMember).where(
                CohortMember.cohort_id == cohort.id, CohortMember.user_id == u["id"]
            )
        )
    ).scalar_one_or_none()
    assert cm is not None
    await _gsvc(ctx).patch(
        g["id"],
        {"Operations": [{"op": "remove", "path": f'members[value eq "{u["id"]}"]'}]},
    )
    cm2 = (
        await db.execute(
            select(CohortMember).where(
                CohortMember.cohort_id == cohort.id, CohortMember.user_id == u["id"]
            )
        )
    ).scalar_one_or_none()
    assert cm2 is None


# ── R7 adversarial-review regression pins ──


@pytest.mark.asyncio
async def test_scim_formula_username_rejected(ctx):
    with pytest.raises(ScimError) as e:
        await _usvc(ctx).create({"userName": "=HYPERLINK(evil)@bad"})
    assert e.value.status == 400 and e.value.scim_type == "invalidValue"
    with pytest.raises(ScimError):
        await _usvc(ctx).create({"userName": "x@nodot"})


# ── R32: SCIM mutation-probe killers ──


@pytest.mark.asyncio
async def test_group_map_role_ceiling_rejects_admin_and_owner(ctx):
    """Mint ceiling: a group_map must never map to admin/owner — adding
    'admin' to ROLE_MAP_ALLOWED would be privilege escalation via IdP."""
    from app.exceptions import AppError

    svc = ScimTokenService(ctx["db"])
    for role in ("admin", "owner"):
        with pytest.raises(AppError) as e:
            await svc.create(
                ctx["org"].id,
                name=f"bad-{role}",
                group_map={"Ops": {"kind": "role", "role": role}},
                created_by=ctx["owner"].id,
            )
        assert e.value.status_code == 422


@pytest.mark.asyncio
async def test_put_deactivation_and_patch_reactivation(ctx):
    """PUT active=false deprovisions exactly like PATCH; PATCH active=true
    restores an archived membership. Display names are trimmed."""
    email = f"put-{uuid.uuid4().hex[:8]}@corp.example.edu"
    res, _ = await _usvc(ctx).create({"userName": email, "displayName": "P"})
    uid = res["id"]
    out = await _usvc(ctx).replace(uid, {"userName": email, "active": "False"})
    assert out["active"] is False
    # PATCH reactivation.
    out2 = await _usvc(ctx).patch(
        uid, {"Operations": [{"op": "replace", "path": "active", "value": True}]}
    )
    assert out2["active"] is True
    # displayName whitespace trimmed on PATCH.
    out3 = await _usvc(ctx).patch(
        uid, {"Operations": [{"op": "replace", "path": "displayName", "value": "  Neat  "}]}
    )
    assert out3["displayName"] == "Neat"


@pytest.mark.asyncio
async def test_group_patch_invalid_op_rejected(ctx):
    g = await _gsvc(ctx).create({"displayName": f"G-{uuid.uuid4().hex[:6]}"})
    with pytest.raises(ScimError) as e:
        await _gsvc(ctx).patch(g["id"], {"Operations": [{"op": "upsert", "value": {}}]})
    assert e.value.status == 400


# ── R52: /Bulk ──


@pytest.mark.asyncio
async def test_bulk_mixed_operations_savepoints_and_fail_on_errors(ctx):
    from app.integrations.services.scim import (
        MAX_BULK_OPERATIONS,
        apply_bulk,
    )

    db, token = ctx["db"], ctx["token"]
    e1 = f"b1-{uuid.uuid4().hex[:8]}@corp.example.edu"
    e2 = f"b2-{uuid.uuid4().hex[:8]}@corp.example.edu"

    out = await apply_bulk(
        db,
        token,
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": [
                {
                    "method": "POST",
                    "path": "/Users",
                    "bulkId": "a",
                    "data": {"userName": e1, "displayName": "B One"},
                },
                {"method": "POST", "path": "/Users", "bulkId": "b", "data": {"userName": e2}},
                # duplicate -> per-op 409, others unaffected (savepoint)
                {"method": "POST", "path": "/Users", "bulkId": "c", "data": {"userName": e1}},
                {
                    "method": "POST",
                    "path": "/Groups",
                    "data": {"displayName": f"BG-{uuid.uuid4().hex[:6]}"},
                },
            ],
        },
    )
    import json as _json

    _json.dumps(out)  # R53 e2e-caught: exc.body (unbound method) crashed render
    assert out["schemas"] == ["urn:ietf:params:scim:api:messages:2.0:BulkResponse"]
    st = [op["status"] for op in out["Operations"]]
    assert st == ["201", "201", "409", "201"]
    uid1 = out["Operations"][0]["location"].removeprefix("/Users/")

    # PATCH deactivate + DELETE inside bulk.
    out2 = await apply_bulk(
        db,
        token,
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": [
                {
                    "method": "PATCH",
                    "path": f"/Users/{uid1}",
                    "data": {"Operations": [{"op": "replace", "path": "active", "value": False}]},
                },
                {"method": "DELETE", "path": f"/Users/{uid1}"},
                {
                    "method": "PUT",
                    "path": "/Groups/01NOPENOPENOPENOPENOPENOPE",
                    "data": {"displayName": "nope"},
                },
                {"method": "TRACE", "path": "/Users"},
            ],
        },
    )
    assert [op["status"] for op in out2["Operations"]] == ["200", "204", "404", "400"]

    # failOnErrors stops after the first failure.
    out3 = await apply_bulk(
        db,
        token,
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "failOnErrors": 1,
            "Operations": [
                {"method": "DELETE", "path": "/Users/01NOPENOPENOPENOPENOPENOPE"},
                {
                    "method": "POST",
                    "path": "/Users",
                    "data": {"userName": f"never-{uuid.uuid4().hex[:6]}@corp.example.edu"},
                },
            ],
        },
    )
    assert len(out3["Operations"]) == 1 and out3["Operations"][0]["status"] == "404"

    # bulkId cross-references unsupported -> per-op 501.
    out4 = await apply_bulk(
        db,
        token,
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": [
                {
                    "method": "POST",
                    "path": "/Groups",
                    "data": {"displayName": "X", "members": [{"value": "bulkId:a"}]},
                },
            ],
        },
    )
    assert out4["Operations"][0]["status"] == "501"

    # Failed-op response carries the real RFC error body and status
    # (kills the swallow-the-body and constant-400 mutants).
    dup = out["Operations"][2]
    assert dup["response"]["status"] == "409"
    assert dup["response"]["scimType"] == "uniqueness"
    assert "urn:ietf:params:scim:api:messages:2.0:Error" in dup["response"]["schemas"]

    # SAVEPOINT isolation: a PATCH that mutates displayName then fails on a
    # bad active value must roll back the mutation — without the savepoint
    # the half-applied displayName would commit with the rest of the bulk.
    e3 = f"b3-{uuid.uuid4().hex[:8]}@corp.example.edu"
    out5 = await apply_bulk(
        db,
        token,
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": [
                {
                    "method": "POST",
                    "path": "/Users",
                    "data": {"userName": e3, "displayName": "Before"},
                },
            ],
        },
    )
    uid3 = out5["Operations"][0]["location"].removeprefix("/Users/")
    out6 = await apply_bulk(
        db,
        token,
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": [
                {
                    "method": "PATCH",
                    "path": f"/Users/{uid3}",
                    "data": {
                        "Operations": [
                            {"op": "replace", "path": "displayName", "value": "HalfApplied"},
                            {"op": "replace", "path": "active", "value": "garbage"},
                        ]
                    },
                },
            ],
        },
    )
    assert out6["Operations"][0]["status"] == "400"
    got = await _usvc(ctx).get(uid3)
    assert got["displayName"] == "Before"  # savepoint rolled the mutation back

    # Caps: schema + op count.
    with pytest.raises(ScimError):
        await apply_bulk(db, token, {"schemas": [], "Operations": [{}]})
    with pytest.raises(ScimError):
        await apply_bulk(
            db,
            token,
            {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
                "Operations": [{"method": "DELETE", "path": "/Users/x"}]
                * (MAX_BULK_OPERATIONS + 1),
            },
        )


@pytest.mark.asyncio
async def test_filter_operator_case_insensitive(ctx):
    """RFC 7644 §3.4.2.2 (R78): 'Eq'/'EQ' must parse like 'eq'."""
    email = f"ci-{uuid.uuid4().hex[:8]}@corp.example.edu"
    await _usvc(ctx).create({"userName": email})
    for op in ("Eq", "EQ"):
        lst = await _usvc(ctx).list(filter_expr=f'userName {op} "{email}"', start_index=1, count=10)
        assert lst["totalResults"] == 1, op


@pytest.mark.asyncio
async def test_group_put_full_replace_okta_dialect(ctx):
    """R79: Okta group push uses PUT — full member-set replace (absent
    members removed, role effects reverted by the shared delta engine),
    rename with uniqueness, 404 on unknown group."""
    e1 = f"gp1-{uuid.uuid4().hex[:8]}@corp.example.edu"
    e2 = f"gp2-{uuid.uuid4().hex[:8]}@corp.example.edu"
    u1, _ = await _usvc(ctx).create({"userName": e1})
    u2, _ = await _usvc(ctx).create({"userName": e2})
    g = await _gsvc(ctx).create(
        {"displayName": f"GP-{uuid.uuid4().hex[:6]}", "members": [{"value": u1["id"]}]}
    )
    out = await _gsvc(ctx).replace(
        g["id"],
        {"displayName": "Renamed Group", "members": [{"value": u2["id"]}]},
    )
    assert out["displayName"] == "Renamed Group"
    assert [m["value"] for m in out["members"]] == [u2["id"]]  # u1 removed

    # Rename collision -> 409.
    g2 = await _gsvc(ctx).create({"displayName": f"GP2-{uuid.uuid4().hex[:6]}"})
    with pytest.raises(ScimError) as exc:
        await _gsvc(ctx).replace(g2["id"], {"displayName": "Renamed Group"})
    assert exc.value.status == 409
    # Unknown group -> 404.
    with pytest.raises(ScimError) as exc2:
        await _gsvc(ctx).replace("01NOPENOPENOPENOPENOPENOPE", {"displayName": "X"})
    assert exc2.value.status == 404


@pytest.mark.asyncio
async def test_list_pagination_edges(ctx):
    """R80: RFC 7644 §3.4.2.4 — count=0 returns totals with no resources;
    out-of-range startIndex returns an empty page, never an error."""
    email = f"pg-{uuid.uuid4().hex[:8]}@corp.example.edu"
    await _usvc(ctx).create({"userName": email})
    out = await _usvc(ctx).list(filter_expr=f'userName eq "{email}"', start_index=1, count=0)
    assert out["totalResults"] == 1 and out["Resources"] == []
    out2 = await _usvc(ctx).list(filter_expr=f'userName eq "{email}"', start_index=99, count=10)
    assert out2["totalResults"] == 1 and out2["Resources"] == []
    g = await _gsvc(ctx).create({"displayName": f"PG-{uuid.uuid4().hex[:6]}"})
    out3 = await _gsvc(ctx).list(start_index=1, count=0)
    assert out3["Resources"] == [] and out3["totalResults"] >= 1
    assert g["id"]


@pytest.mark.asyncio
async def test_scim_event_feed_mirrors_lifecycle(ctx):
    """R91: provision/deprovision/reactivate all mirror into the mesh with
    ids only — no email/display PII in event data."""
    from sqlalchemy import select as _select

    from app.integrations.models import IntegrationEvent

    db = ctx["db"]
    email = f"feed-{uuid.uuid4().hex[:8]}@corp.example.edu"
    res, _ = await _usvc(ctx).create({"userName": email, "displayName": "Feed User"})
    uid = res["id"]
    await _usvc(ctx).patch(
        uid, {"Operations": [{"op": "replace", "path": "active", "value": False}]}
    )
    await _usvc(ctx).patch(
        uid, {"Operations": [{"op": "replace", "path": "active", "value": True}]}
    )
    # PUT-arm reactivation emits too (kills the PUT-site mutant).
    await _usvc(ctx).replace(uid, {"userName": email, "active": False})
    await _usvc(ctx).replace(uid, {"userName": email, "active": True})
    events = (
        (await db.execute(_select(IntegrationEvent).where(IntegrationEvent.subject == uid)))
        .scalars()
        .all()
    )
    types = [e.type for e in events]
    for expected in (
        "com.openskill.org.scim.provisioned.v1",
        "com.openskill.org.scim.deprovisioned.v1",
        "com.openskill.org.scim.reactivated.v1",
    ):
        assert expected in types, types
    assert types.count("com.openskill.org.scim.reactivated.v1") == 2  # PATCH + PUT arms
    for e in events:
        assert set(e.data) == {"user_id", "token_id"}  # ids only, no PII
        assert email not in str(e.data)


@pytest.mark.asyncio
async def test_user_list_paginates_at_sql_level(ctx):
    """R162: list pages via SQL offset/limit — total is stable across pages,
    pages do not overlap, and successive pages advance."""
    svc = _usvc(ctx)
    for _ in range(5):
        await svc.create(
            {"userName": f"pg-{uuid.uuid4().hex[:8]}@scim.example.edu", "active": True}
        )

    p1 = await svc.list(filter_expr=None, start_index=1, count=2)
    p2 = await svc.list(filter_expr=None, start_index=3, count=2)
    p3 = await svc.list(filter_expr=None, start_index=5, count=2)
    assert p1["totalResults"] == p2["totalResults"] == p3["totalResults"]
    assert p1["totalResults"] >= 5
    ids1 = {r["id"] for r in p1["Resources"]}
    ids2 = {r["id"] for r in p2["Resources"]}
    ids3 = {r["id"] for r in p3["Resources"]}
    assert len(ids1) == 2 and len(ids2) == 2
    assert not (ids1 & ids2) and not (ids2 & ids3) and not (ids1 & ids3)
    # count=0 is a legitimate "just tell me the total" probe
    p0 = await svc.list(filter_expr=None, start_index=1, count=0)
    assert p0["Resources"] == [] and p0["totalResults"] >= 5


@pytest.mark.asyncio
async def test_concurrent_scim_create_same_username(ctx):
    """R167: two concurrent SCIM creates of the same new userName — exactly
    one User lands; the loser gets a clean SCIM 409 (uniqueness), never a
    raw 500 / poisoned session."""
    import asyncio

    from sqlalchemy import func

    from app.core.database import AsyncSessionLocal
    from app.integrations.services.scim import ScimError, ScimUserService
    from app.models.user import User as _User

    await ctx["db"].commit()  # concurrent sessions must SEE the org + token
    token = ctx["token"]
    username = f"scim-race-{uuid.uuid4().hex[:8]}@scim.example.edu"

    async def create():
        async with AsyncSessionLocal() as own:
            try:
                await ScimUserService(own, token).create({"userName": username, "active": True})
                await own.commit()
                return "created"
            except ScimError as e:
                return e.status

    results = await asyncio.gather(create(), create(), return_exceptions=True)
    for r in results:
        assert not isinstance(r, BaseException), f"raw crash (not a clean 409): {r!r}"
    assert "created" in results
    assert 409 in results, f"expected one 409, got {results}"

    n = (
        await ctx["db"].execute(
            select(func.count()).select_from(_User).where(func.lower(_User.email) == username)
        )
    ).scalar_one()
    assert n == 1


@pytest.mark.asyncio
async def test_concurrent_scim_group_create_same_name(ctx):
    """R176: two concurrent SCIM group creates with the same displayName —
    one lands, the loser gets a clean SCIM 409 uniqueness, never a 500."""
    import asyncio

    from sqlalchemy import func

    from app.core.database import AsyncSessionLocal
    from app.integrations.models.scim import ScimGroup
    from app.integrations.services.scim import ScimError, ScimGroupService

    await ctx["db"].commit()
    token = ctx["token"]
    name = f"grp-race-{uuid.uuid4().hex[:8]}"

    async def create():
        async with AsyncSessionLocal() as own:
            try:
                await ScimGroupService(own, token).create({"displayName": name})
                await own.commit()
                return "created"
            except ScimError as e:
                return e.status

    results = await asyncio.gather(create(), create(), return_exceptions=True)
    for r in results:
        assert not isinstance(r, BaseException), f"raw crash (not a clean 409): {r!r}"
    assert "created" in results and 409 in results, f"got {results}"

    n = (
        await ctx["db"].execute(
            select(func.count())
            .select_from(ScimGroup)
            .where(ScimGroup.org_id == ctx["org"].id, ScimGroup.display_name == name)
        )
    ).scalar_one()
    assert n == 1


@pytest.mark.asyncio
async def test_scim_group_patch_rename_collision_clean_409(ctx):
    """R192: PATCH-renaming a group onto an existing name returns a clean SCIM
    409 (uniqueness), not a 500, and does not poison the session."""
    from app.integrations.services.scim import ScimError, ScimGroupService

    svc = ScimGroupService(ctx["db"], ctx["token"])
    g1 = await svc.create({"displayName": f"grp-a-{uuid.uuid4().hex[:6]}"})
    name_b = f"grp-b-{uuid.uuid4().hex[:6]}"
    g2 = await svc.create({"displayName": name_b})
    await ctx["db"].flush()

    with pytest.raises(ScimError) as e:
        await svc.patch(
            g2["id"],
            {"Operations": [{"op": "replace", "path": "displayName", "value": g1["displayName"]}]},
        )
    assert e.value.status == 409

    # Session still usable: a legit rename of g2 works.
    ok = await svc.patch(
        g2["id"],
        {"Operations": [{"op": "replace", "path": "displayName", "value": name_b + "-2"}]},
    )
    assert ok["displayName"] == name_b + "-2"


@pytest.mark.asyncio
async def test_bulk_fail_on_errors_must_be_nonnegative_int(ctx):
    """R269 (survivor pin): failOnErrors is validated as a non-negative
    integer — -1 or a string yields a clean 400, never a bogus early stop
    (a negative threshold would make `failures >= fail_on` true from the
    first operation)."""
    from app.integrations.services.scim import ScimError, apply_bulk

    db, token = ctx["db"], ctx["token"]
    for bad in (-1, "2"):
        with pytest.raises(ScimError) as e:
            await apply_bulk(
                db,
                token,
                {
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
                    "failOnErrors": bad,
                    "Operations": [
                        {
                            "method": "POST",
                            "path": "/Users",
                            "data": {"userName": f"fo-{uuid.uuid4().hex[:8]}@corp.example.edu"},
                        },
                    ],
                },
            )
        assert e.value.status == 400


@pytest.mark.asyncio
async def test_patch_operations_must_be_nonempty_list(ctx):
    """R274 (survivor pins): user-PATCH and group-PATCH validate the
    Operations envelope — missing, non-list, or empty yields a clean
    ScimError 400, never an iteration crash (IdPs send garbage)."""
    res, _ = await _usvc(ctx).create({"userName": f"po-{uuid.uuid4().hex[:8]}@corp.example.edu"})
    g = await _gsvc(ctx).create({"displayName": f"PG-{uuid.uuid4().hex[:6]}"})
    for bad in ({}, {"Operations": "x"}, {"Operations": []}):
        with pytest.raises(ScimError) as e:
            await _usvc(ctx).patch(res["id"], bad)
        assert e.value.status == 400
        with pytest.raises(ScimError) as e:
            await _gsvc(ctx).patch(g["id"], bad)
        assert e.value.status == 400


@pytest.mark.asyncio
async def test_scim_token_cross_org_walls(ctx):
    """R276 (survivor pins, IDOR class): org B can neither revoke nor
    rewrite the group_map of org A's SCIM token — uniform 404."""
    from app.exceptions import AppError
    from app.integrations.services.scim import ScimTokenService

    db, token_a = ctx["db"], ctx["token"]
    owner_b = await _user(db)
    org_b = await _org(db, owner_b)
    svc = ScimTokenService(db)
    with pytest.raises(AppError) as e:
        await svc.update_group_map(org_b.id, token_a.id, {})
    assert e.value.code == "SCIM_TOKEN_NOT_FOUND"
    assert e.value.status_code == 404
    with pytest.raises(AppError) as e:
        await svc.revoke(org_b.id, token_a.id)
    assert e.value.code == "SCIM_TOKEN_NOT_FOUND"
    assert e.value.status_code == 404
    assert token_a.revoked_at is None


@pytest.mark.asyncio
async def test_group_map_foreign_cohort_walls(ctx):
    """R277 (SECURITY): a cohort id in group_map is a cross-org capability.
    (1) create/update_group_map refuse a cohort belonging to another org;
    (2) even with a foreign id smuggled into group_map, the group-LEAVE
    path must not delete the user's membership in the other org's cohort
    (the join path is org-checked via CohortService; the delete path is
    now scoped too)."""
    from app.exceptions import AppError
    from app.models.cohort import CohortMember, CohortRole
    from app.models.organization import MemberStatus, OrgMember, OrgRole
    from app.services.cohort import CohortService

    db, owner = ctx["db"], ctx["owner"]
    org_b = ctx["org"]
    owner_a = await _user(db)
    org_a = await _org(db, owner_a)
    cohort_a = await CohortService(db).create_cohort(
        org_id=org_a.id, name=f"A {ULID()}", description=None, created_by=owner_a.id
    )

    # (1) validation walls at create and update.
    svc = ScimTokenService(db)
    bad_map = {"G": {"kind": "cohort", "id": cohort_a.id}}
    with pytest.raises(AppError) as e:
        await svc.create(org_b.id, name="bad", group_map=bad_map, created_by=owner.id)
    assert e.value.code == "SCIM_GROUP_MAP_INVALID"
    with pytest.raises(AppError) as e:
        await svc.update_group_map(org_b.id, ctx["token"].id, bad_map)
    assert e.value.code == "SCIM_GROUP_MAP_INVALID"

    # (2) leave path with a smuggled foreign id: org A's membership survives.
    ctx["token"].group_map = bad_map  # direct set, bypassing validation
    await db.flush()
    email = f"fx-{uuid.uuid4().hex[:8]}@corp.example.edu"
    u, _ = await _usvc(ctx).create({"userName": email})
    db.add(
        OrgMember(
            org_id=org_a.id, user_id=u["id"], role=OrgRole.STUDENT, status=MemberStatus.ACTIVE
        )
    )
    db.add(CohortMember(cohort_id=cohort_a.id, user_id=u["id"], role=CohortRole.LEARNER))
    await db.flush()
    g = await _gsvc(ctx).create({"displayName": "G", "members": [{"value": u["id"]}]})
    await _gsvc(ctx).patch(
        g["id"],
        {"Operations": [{"op": "remove", "path": f'members[value eq "{u["id"]}"]'}]},
    )
    still = (
        await db.execute(
            select(CohortMember).where(
                CohortMember.cohort_id == cohort_a.id, CohortMember.user_id == u["id"]
            )
        )
    ).scalar_one_or_none()
    assert still is not None  # foreign cohort untouched


@pytest.mark.asyncio
async def test_unicode_displayname_roundtrip(ctx):
    """R292: CJK + emoji display names survive SCIM create/get and the
    member resource rendering (truncation is by CHARACTERS, not bytes —
    a byte-slice would shear a multibyte sequence)."""
    name = "李小龙 🐉 Ẑoë"
    email = f"uni-{uuid.uuid4().hex[:8]}@corp.example.edu"
    res, created = await _usvc(ctx).create({"userName": email, "displayName": name})
    assert created
    got = await _usvc(ctx).get(res["id"])
    assert got["displayName"] == name
    # 100-char cap cuts characters, never bytes: a 120-char CJK name stays
    # valid text of exactly 100 chars.
    long_name = "汉" * 120
    email2 = f"uni2-{uuid.uuid4().hex[:8]}@corp.example.edu"
    res2, _ = await _usvc(ctx).create({"userName": email2, "displayName": long_name})
    got2 = await _usvc(ctx).get(res2["id"])
    assert got2["displayName"] == "汉" * 100


@pytest.mark.asyncio
async def test_scim_cannot_deprovision_last_owner(ctx):
    """R330 (found by the scale smoke bricking its own org): the IdP must
    not archive the LAST active owner — every admin surface is
    owner/admin-gated and the deprovision also revokes all their sessions.
    With a second owner present, deprovisioning one owner is allowed."""
    from app.exceptions import AppError  # noqa: F401 (symmetry with suite)
    from app.models.organization import OrgRole

    db, owner, org = ctx["db"], ctx["owner"], ctx["org"]
    # the owner appears in the SCIM directory; find their SCIM id by email
    lst = await _usvc(ctx).list(filter_expr=f'userName eq "{owner.email}"', start_index=1, count=10)
    assert lst["totalResults"] == 1
    owner_scim_id = lst["Resources"][0]["id"]

    # sole owner: PATCH active=false AND DELETE both refuse with 409
    with pytest.raises(ScimError) as e:
        await _usvc(ctx).patch(
            owner_scim_id,
            {"Operations": [{"op": "replace", "path": "active", "value": False}]},
        )
    assert e.value.status == 409
    with pytest.raises(ScimError) as e:
        await _usvc(ctx).delete(owner_scim_id)
    assert e.value.status == 409
    member = (
        await db.execute(
            select(OrgMember).where(OrgMember.org_id == org.id, OrgMember.user_id == owner.id)
        )
    ).scalar_one()
    assert member.status == MemberStatus.ACTIVE  # untouched

    # add a SECOND active owner -> deprovisioning the first is now allowed
    u2 = await _user(db)
    db.add(OrgMember(org_id=org.id, user_id=u2.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE))
    await db.flush()
    await _usvc(ctx).delete(owner_scim_id)
    await db.refresh(member)
    assert member.status == MemberStatus.ARCHIVED


@pytest.mark.asyncio
async def test_bulk_and_members_reject_non_container_types(ctx):
    """R353 (fuzz-found 500s): `in`/iteration over an untrusted
    non-container raises TypeError — schemas=1e308 crashed /Bulk before
    validation, and members=3.14 would crash group PUT the same way.
    Both must be clean 400s."""
    from app.integrations.services.scim import apply_bulk

    db, token = ctx["db"], ctx["token"]
    with pytest.raises(ScimError) as e:
        await apply_bulk(db, token, {"schemas": 1e308, "Operations": [{}]})
    assert e.value.status == 400

    g = await _gsvc(ctx).create({"displayName": f"NC-{uuid.uuid4().hex[:6]}"})
    with pytest.raises(ScimError) as e:
        await _gsvc(ctx).replace(g["id"], {"displayName": "NC2", "members": 3.14})
    assert e.value.status == 400


@pytest.mark.asyncio
async def test_patch_path_must_be_string(ctx):
    """R358 (fuzz-found 500): a non-string op path (123) reached
    str.strip() — clean 400 on both user and group PATCH now."""
    email = f"pp-{uuid.uuid4().hex[:8]}@corp.example.edu"
    u, _ = await _usvc(ctx).create({"userName": email})
    g = await _gsvc(ctx).create({"displayName": f"PPG-{uuid.uuid4().hex[:6]}"})
    for svc, rid in ((_usvc(ctx), u["id"]), (_gsvc(ctx), g["id"])):
        with pytest.raises(ScimError) as e:
            await svc.patch(rid, {"Operations": [{"op": "remove", "path": 123}]})
        assert e.value.status == 400


async def test_group_list_filter_displayname_and_externalid(ctx):
    """R391: /Groups silently IGNORED the filter param — Okta dedups groups
    with `displayName eq "..."` before creating, so an ignored filter
    returned the whole directory and let the IdP duplicate or mis-match
    groups. Filter must narrow (case-insensitive displayName, exact
    externalId) and reject unknown attributes loudly."""
    svc = _gsvc(ctx)
    await svc.create({"displayName": "Engineering", "externalId": "ext-eng"})
    await svc.create({"displayName": "Design", "externalId": "ext-des"})

    out = await svc.list(start_index=1, count=100, filter_expr='displayName eq "engineering"')
    assert out["totalResults"] == 1
    assert out["Resources"][0]["displayName"] == "Engineering"

    out = await svc.list(start_index=1, count=100, filter_expr='externalId eq "ext-des"')
    assert out["totalResults"] == 1
    assert out["Resources"][0]["displayName"] == "Design"

    out = await svc.list(start_index=1, count=100, filter_expr='displayName eq "nope"')
    assert out["totalResults"] == 0 and out["Resources"] == []

    import pytest as _pytest

    from app.integrations.services.scim import ScimError

    with _pytest.raises(ScimError) as e:
        await svc.list(start_index=1, count=100, filter_expr='members eq "x"')
    assert e.value.status == 400

    # no filter still lists everything
    out = await svc.list(start_index=1, count=100)
    assert out["totalResults"] == 2


async def test_group_patch_member_remove_filter_is_case_insensitive(ctx):
    """R409: the filtered member-remove op `Members[value eq "..."]` must
    match regardless of the attribute-name case (the rest of the PATCH
    grammar is case-insensitive) — a case-varying IdP's member removal
    must not silently no-op. The captured member id stays case-exact."""
    u, _ = await _usvc(ctx).create({"userName": f"ci-{uuid.uuid4().hex[:8]}@corp.example.edu"})
    svc = _gsvc(ctx)
    grp = await svc.create(
        {"displayName": f"Eng-{uuid.uuid4().hex[:6]}", "members": [{"value": u["id"]}]}
    )
    assert u["id"] in [m["value"] for m in grp["members"]]

    # capital "Members" (and the exact-case id) must still remove
    out = await svc.patch(
        grp["id"],
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [{"op": "remove", "path": f'Members[value eq "{u["id"]}"]'}],
        },
    )
    assert u["id"] not in [m["value"] for m in out["members"]]


@pytest.mark.asyncio
async def test_bulk_users_put_and_groups_put_patch_delete_success(ctx):
    """R425: the bulk dispatcher's Users-PUT and Groups-PUT/PATCH/DELETE
    SUCCESS arms had never executed (only the 404/400 arms were pinned)."""
    from app.integrations.services.scim import apply_bulk

    db, token = ctx["db"], ctx["token"]
    email = f"bp-{uuid.uuid4().hex[:8]}@corp.example.edu"
    u, _ = await _usvc(ctx).create({"userName": email, "displayName": "Before"})
    g = await _gsvc(ctx).create({"displayName": f"BG-{uuid.uuid4().hex[:6]}"})

    out = await apply_bulk(
        db,
        token,
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": [
                {
                    "method": "PUT",
                    "path": f"/Users/{u['id']}",
                    "data": {"userName": email, "displayName": "After PUT", "active": True},
                },
                {
                    "method": "PUT",
                    "path": f"/Groups/{g['id']}",
                    "data": {"displayName": f"BG2-{uuid.uuid4().hex[:6]}"},
                },
                {
                    "method": "PATCH",
                    "path": f"/Groups/{g['id']}",
                    "data": {
                        "Operations": [
                            {
                                "op": "add",
                                "path": "members",
                                "value": [{"value": u["id"]}],
                            }
                        ]
                    },
                },
                {"method": "DELETE", "path": f"/Groups/{g['id']}"},
            ],
        },
    )
    assert [op["status"] for op in out["Operations"]] == ["200", "200", "200", "204"]
    assert out["Operations"][0]["location"] == f"/Users/{u['id']}"
    refreshed = await _usvc(ctx).get(u["id"])
    assert refreshed["displayName"] == "After PUT"


@pytest.mark.asyncio
async def test_user_patch_external_id_add_and_remove(ctx):
    """R425: patch's externalId add (upsert link) and remove (clear link)
    arms, plus the non-dict operation reject."""
    from app.integrations.services.scim import ScimError

    email = f"xi-{uuid.uuid4().hex[:8]}@corp.example.edu"
    u, _ = await _usvc(ctx).create({"userName": email})

    res = await _usvc(ctx).patch(
        u["id"],
        {"Operations": [{"op": "add", "path": "externalId", "value": "ext-r425"}]},
    )
    assert res["externalId"] == "ext-r425"

    res = await _usvc(ctx).patch(
        u["id"], {"Operations": [{"op": "remove", "path": "externalId"}]}
    )
    assert res.get("externalId") in (None, "")

    with pytest.raises(ScimError):
        await _usvc(ctx).patch(u["id"], {"Operations": ["not-a-dict"]})


@pytest.mark.asyncio
async def test_group_map_validation_rejects_and_token_scoping(ctx):
    """R425: every _validate_group_map reject arm, including the mint
    ceiling (owner/admin can never be group-mapped), and update_group_map's
    cross-org 404."""
    from app.exceptions import AppError
    from app.integrations.services.scim import ScimTokenService

    db, org, token = ctx["db"], ctx["org"], ctx["token"]
    svc = ScimTokenService(db)

    for bad in (
        {"G": "not-a-dict"},
        {"G": {"kind": "nonsense"}},
        {"G": {"kind": "cohort"}},  # cohort id required
        {"G": {"kind": "role", "role": "owner"}},  # mint ceiling
        {"G": {"kind": "role", "role": "admin"}},  # mint ceiling
    ):
        with pytest.raises(AppError) as exc:
            await svc.update_group_map(org.id, token.id, bad)
        assert exc.value.code == "SCIM_GROUP_MAP_INVALID"

    # Valid role map lands.
    tok = await svc.update_group_map(
        org.id, token.id, {"Students": {"kind": "role", "role": "student"}}
    )
    assert tok.group_map == {"Students": {"kind": "role", "role": "student"}}

    # Wrong org (existence oracle): uniform 404.
    with pytest.raises(AppError) as exc:
        await svc.update_group_map("01FAKEORGFAKEORGFAKEORGFAK", token.id, {})
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_user_patch_active_and_displayname_grammar(ctx):
    """R450 (mutation-kill): the user-PATCH op grammar's security-critical
    arms. active=False on an active member deprovisions; active=True on an
    active member must NOT deprovision (kills the `is False and active` ->
    `or` mutant); active=True on an inactive member reactivates; an empty
    displayname string is ignored (kills the `isinstance and strip` -> `or`
    mutant); and non-dict/unsupported/invalid-active ops carry exact 400s."""
    from app.integrations.services.scim import ScimError
    from app.models.organization import MemberStatus

    usvc = _usvc(ctx)

    # active=True on an ACTIVE member -> stays active, NOT deprovisioned.
    u1, _ = await usvc.create({"userName": f"a1-{uuid.uuid4().hex[:6]}@corp.example.edu"})
    await usvc.patch(u1["id"], {"Operations": [{"op": "replace", "path": "active", "value": True}]})
    _, m1 = await usvc._member_for(u1["id"])
    assert m1.status == MemberStatus.ACTIVE

    # active=False on an ACTIVE member -> deprovisioned.
    u2, _ = await usvc.create({"userName": f"a2-{uuid.uuid4().hex[:6]}@corp.example.edu"})
    await usvc.patch(u2["id"], {"Operations": [{"op": "replace", "path": "active", "value": False}]})
    _, m2 = await usvc._member_for(u2["id"])
    assert m2.status != MemberStatus.ACTIVE

    # active=True on the now-inactive member -> reactivated.
    await usvc.patch(u2["id"], {"Operations": [{"op": "replace", "path": "active", "value": True}]})
    _, m2b = await usvc._member_for(u2["id"])
    assert m2b.status == MemberStatus.ACTIVE

    # Empty displayname string is ignored (no overwrite to blank).
    u3, _ = await usvc.create(
        {"userName": f"a3-{uuid.uuid4().hex[:6]}@corp.example.edu", "displayName": "Keep Me"}
    )
    await usvc.patch(
        u3["id"], {"Operations": [{"op": "replace", "path": "displayName", "value": "  "}]}
    )
    got = await usvc.get(u3["id"])
    assert got["displayName"] == "Keep Me"

    # Exact 400s.
    with pytest.raises(ScimError) as e:
        await usvc.patch(u3["id"], {"Operations": ["not-a-dict"]})
    assert e.value.status == 400
    with pytest.raises(ScimError) as e:
        await usvc.patch(u3["id"], {"Operations": [{"op": "frobnicate"}]})
    assert e.value.status == 400
    with pytest.raises(ScimError) as e:
        await usvc.patch(
            u3["id"], {"Operations": [{"op": "replace", "path": "active", "value": "maybe"}]}
        )
    assert e.value.status == 400


@pytest.mark.asyncio
async def test_group_patch_displayname_and_filtered_remove_grammar(ctx):
    """R450 (mutation-kill): group-PATCH grammar. A 'remove' op on displayName
    must NOT rename (kills the `displayname and name in add/replace` -> `or`
    mutant), and a FILTERED member path with a non-remove op must NOT remove a
    member (kills the `m and name == remove` -> `or` mutant)."""
    usvc, gsvc = _usvc(ctx), _gsvc(ctx)
    u, _ = await usvc.create({"userName": f"gm-{uuid.uuid4().hex[:6]}@corp.example.edu"})
    g = await gsvc.create(
        {"displayName": f"G-{uuid.uuid4().hex[:6]}", "members": [{"value": u["id"]}]}
    )
    orig_name = g["displayName"]

    # 'remove' on displayName is NOT a rename (rename only on add/replace).
    await gsvc.patch(
        g["id"], {"Operations": [{"op": "remove", "path": "displayName", "value": "WIPED"}]}
    )
    after = await gsvc.get(g["id"])
    assert after["displayName"] == orig_name

    # A filtered member path with op='add' must NOT remove the member.
    await gsvc.patch(
        g["id"],
        {"Operations": [{"op": "add", "path": f'members[value eq "{u["id"]}"]'}]},
    )
    after2 = await gsvc.get(g["id"])
    member_ids = {m["value"] for m in after2.get("members", [])}
    assert u["id"] in member_ids  # still a member; the add-with-filter didn't remove


@pytest.mark.asyncio
async def test_group_patch_replace_members_delta_and_rename_collision(ctx):
    """R451 (mutation-kill): the group-PATCH replace-members full-set delta
    (op=replace, path=members computes add=target-current, remove=current-
    target — a never-exercised path) and the rename-collision 409."""
    from app.integrations.services.scim import ScimError

    usvc, gsvc = _usvc(ctx), _gsvc(ctx)
    a, _ = await usvc.create({"userName": f"ma-{uuid.uuid4().hex[:6]}@corp.example.edu"})
    b, _ = await usvc.create({"userName": f"mb-{uuid.uuid4().hex[:6]}@corp.example.edu"})
    c, _ = await usvc.create({"userName": f"mc-{uuid.uuid4().hex[:6]}@corp.example.edu"})

    g = await gsvc.create(
        {"displayName": f"G1-{uuid.uuid4().hex[:6]}",
         "members": [{"value": a["id"]}, {"value": b["id"]}]}
    )
    # Replace the full member set with {B, C}: A drops, C joins, B stays.
    await gsvc.patch(
        g["id"],
        {"Operations": [
            {"op": "replace", "path": "members",
             "value": [{"value": b["id"]}, {"value": c["id"]}]}
        ]},
    )
    after = await gsvc.get(g["id"])
    ids = {m["value"] for m in after.get("members", [])}
    assert ids == {b["id"], c["id"]}  # delta applied: -A +C, B kept

    # Rename collision: a second group, then rename g onto its name -> 409.
    other = await gsvc.create({"displayName": f"Taken-{uuid.uuid4().hex[:6]}"})
    with pytest.raises(ScimError) as e:
        await gsvc.patch(
            g["id"],
            {"Operations": [
                {"op": "replace", "path": "displayName", "value": other["displayName"]}
            ]},
        )
    assert e.value.status == 409


@pytest.mark.asyncio
async def test_group_patch_nondict_op_and_user_reactivate_guard(ctx):
    """R452 (mutation-kill): a non-dict op in a GROUP patch -> exact 400; and
    a non-active user-patch op (displayName) on an INACTIVE member must NOT
    reactivate it (kills the reactivate-guard `is True and not-active` -> `or`
    mutant — under or, any op on an inactive member would revive it)."""
    from app.integrations.services.scim import ScimError
    from app.models.organization import MemberStatus

    usvc, gsvc = _usvc(ctx), _gsvc(ctx)

    g = await gsvc.create({"displayName": f"G-{uuid.uuid4().hex[:6]}"})
    with pytest.raises(ScimError) as e:
        await gsvc.patch(g["id"], {"Operations": [12345]})
    assert e.value.status == 400

    # Deactivate a user, then PATCH only its displayName -> stays inactive.
    u, _ = await usvc.create({"userName": f"ra-{uuid.uuid4().hex[:6]}@corp.example.edu"})
    await usvc.patch(u["id"], {"Operations": [{"op": "replace", "path": "active", "value": False}]})
    _, m = await usvc._member_for(u["id"])
    assert m.status != MemberStatus.ACTIVE
    await usvc.patch(
        u["id"], {"Operations": [{"op": "replace", "path": "displayName", "value": "Renamed"}]}
    )
    _, m2 = await usvc._member_for(u["id"])
    assert m2.status != MemberStatus.ACTIVE  # displayName op did NOT reactivate


@pytest.mark.asyncio
async def test_scim_audit_swallows_mesh_emit_failure(ctx, monkeypatch):
    """R465: ScimUserService._audit is best-effort — a mesh emit failure must
    be swallowed, never propagate and fail the deprovision. (Also guards the
    `event=` structlog-collision bug: the except arm itself must not TypeError.)"""
    import app.integrations.facade as facade
    from app.models.organization import MemberStatus

    usvc = _usvc(ctx)
    u, _ = await usvc.create({"userName": f"au-{uuid.uuid4().hex[:6]}@corp.example.edu"})

    async def boom(*a, **k):
        raise RuntimeError("mesh down")

    monkeypatch.setattr(facade, "emit_event", boom)
    # active=False -> deprovision -> _audit emits -> emit raises -> swallowed.
    await usvc.patch(u["id"], {"Operations": [{"op": "replace", "path": "active", "value": False}]})
    _, m = await usvc._member_for(u["id"])
    assert m.status != MemberStatus.ACTIVE  # deprovision completed despite emit failure


@pytest.mark.asyncio
async def test_scim_create_replace_tolerate_nondict_name(ctx):
    """R473 (R471 class): a malformed IdP may send the SCIM `name` attribute as
    a string (not the {formatted: ...} object). create/replace must tolerate it
    (fall back to displayName or the userName local part), never crash with
    AttributeError and 500 the provisioning request."""
    usvc = _usvc(ctx)

    # create with name as a bare string -> no crash; display falls back.
    email = f"nd-{uuid.uuid4().hex[:6]}@corp.example.edu"
    res, created = await usvc.create({"userName": email, "name": "John Doe String"})
    assert created and res["userName"] == email
    assert isinstance(res.get("displayName"), str) and res["displayName"]

    # create with name as other non-dict types -> no crash.
    for bad in (42, ["a"], True):
        e2 = f"nd{uuid.uuid4().hex[:6]}@corp.example.edu"
        r2, _ = await usvc.create({"userName": e2, "name": bad})
        assert r2["userName"] == e2

    # replace with name as a string -> no crash; displayName override wins.
    out = await usvc.replace(
        res["id"], {"userName": email, "name": "ignored-string", "displayName": "Real Name"}
    )
    assert out["displayName"] == "Real Name"
