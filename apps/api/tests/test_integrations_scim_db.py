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
            org.id, name="bad", group_map={"G": {"kind": "role", "role": "owner"}},
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
    lst = await _usvc(ctx).list(
        filter_expr=f'userName eq "{email}"', start_index=1, count=100
    )
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
            select(OrgMember).where(
                OrgMember.org_id == ctx["org"].id, OrgMember.user_id == u["id"]
            )
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
    g = await _gsvc(ctx).create(
        {"displayName": "Class A", "members": [{"value": u["id"]}]}
    )
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
