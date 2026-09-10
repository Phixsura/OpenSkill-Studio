"""P9 DB tests: guest links, principals, review flow, isolation matrix."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.client_portal import (
    ClientPortalMember,
    ClientShare,
)
from app.controlplane.models.plan import TenantEntitlementOverride
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import client_portal as portal_svc
from app.controlplane.services.audit import Actor
from app.controlplane.services.entitlements import invalidate_cache
from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token, hash_password
from app.exceptions import AppError
from app.models.client_brief import BriefStatus, ClientBrief
from app.models.project import (
    Project,
    Submission,
    SubmissionComment,
    SubmissionItem,
    SubmissionStatus,
)
from app.models.user import User, UserRole, UserStatus
from app.services.organization import OrgService


@pytest.fixture
async def db():
    from app.core.database import engine

    # R134 follow-up: a preceding file can leave pool connections bound to its
    # (now closed) event loop — the first checkout here then dies with
    # "Event loop is closed". Abandon any stale pool without touching the
    # dead-loop connections (close=False), then open fresh ones on this loop.
    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_user(db) -> User:
    user = User(
        email=f"cp9-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP9 Instructor",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_project_env(db, user):
    """org (portal-entitled tenant) + brief + project + submitted submission."""
    svc = OrgService(db)
    org = await svc.create(
        name=f"P9 {ULID()}",
        slug=f"p9-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    db.add(
        TenantEntitlementOverride(
            tenant_id=tenant.id,
            key="client_portal",
            value={"v": True},
            reason="test",
        )
    )
    await db.flush()
    await invalidate_cache(tenant.id)
    brief = ClientBrief(
        org_id=org.id,
        title="Acme rebrand",
        slug=f"acme-{str(ULID()).lower()}",
        client_name="Acme Inc",
        project_type="brand_visuals",
        objective="Launch visuals for the autumn campaign",
        budget_range="$10k-20k",  # HIDDEN field — leak-tested
        brand_guidelines="internal only",
        status=BriefStatus.REVIEW,
        created_by=user.id,
    )
    db.add(brief)
    await db.flush()
    project = Project(
        org_id=org.id,
        title="Acme production",
        slug=f"acmep-{str(ULID()).lower()}",
        description="d",
        instructions="i",
        rubric={"criteria": []},
        client_brief_id=brief.id,
        created_by=user.id,
    )
    db.add(project)
    await db.flush()
    submission = Submission(
        org_id=org.id,
        project_id=project.id,
        user_id=user.id,
        version=1,
        status=SubmissionStatus.SUBMITTED,
        submitted_at=datetime.now(UTC),
    )
    db.add(submission)
    await db.flush()
    return org, tenant, brief, project, submission


def _actor(user):
    return Actor(user_id=user.id, type="tenant")


async def _guest_auth(db, project, user, role="approver") -> str:
    link, raw = await portal_svc.create_guest_link(
        db,
        project_id=project.id,
        label="Acme CMO",
        email=None,
        role=role,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        actor=_actor(user),
    )
    token, _ = await portal_svc.exchange_guest_token(db, raw, None)
    return f"Bearer {token}"


# ── Guest link lifecycle ─────────────────────────────────────


@pytest.mark.asyncio
async def test_guest_exchange_and_uniform_401(db):
    user = await _mk_user(db)
    _, _, _, project, _ = await _mk_project_env(db, user)
    link, raw = await portal_svc.create_guest_link(
        db,
        project_id=project.id,
        label="Client",
        email="cmo@acme.com",
        role="reviewer",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        actor=_actor(user),
    )
    # Raw token is hashed at rest
    assert raw not in (link.token_hash or "")
    # Email-bound: wrong email → same 401 as bad token
    with pytest.raises(AppError) as e1:
        await portal_svc.exchange_guest_token(db, raw, "wrong@acme.com")
    assert e1.value.code == "GUEST_LINK_INVALID"
    token, ctx = await portal_svc.exchange_guest_token(db, raw, "CMO@acme.com")
    assert ctx["role"] == "reviewer"
    assert link.use_count == 1
    # Bad token → identical 401
    with pytest.raises(AppError) as e2:
        await portal_svc.exchange_guest_token(db, "not-a-real-token-aaaaaaaaaa", None)
    assert e2.value.code == "GUEST_LINK_INVALID"
    # Expired link → identical 401
    link.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await db.flush()
    with pytest.raises(AppError) as e3:
        await portal_svc.exchange_guest_token(db, raw, "cmo@acme.com")
    assert e3.value.code == "GUEST_LINK_INVALID"


@pytest.mark.asyncio
async def test_revocation_is_immediate(db):
    user = await _mk_user(db)
    _, _, _, project, _ = await _mk_project_env(db, user)
    link, raw = await portal_svc.create_guest_link(
        db,
        project_id=project.id,
        label=None,
        email=None,
        role="approver",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        actor=_actor(user),
    )
    token, _ = await portal_svc.exchange_guest_token(db, raw, None)
    auth = f"Bearer {token}"
    principal = await portal_svc.get_client_principal(db, project.id, auth)
    assert principal.kind == "guest"
    # Revoke → the SAME token dies on the next request (per-request recheck)
    link.revoked_at = datetime.now(UTC)
    await db.flush()
    with pytest.raises(AppError) as exc:
        await portal_svc.get_client_principal(db, project.id, auth)
    assert exc.value.code == "CLIENT_ACCESS_DENIED"
    # 401 (dead credential → UI bounces to access page), NOT 403 (role gate
    # on a live session) — the portal frontend only ends the session on 401.
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_cross_project_token_uniform_404(db):
    user = await _mk_user(db)
    _, _, _, project_a, _ = await _mk_project_env(db, user)
    _, _, _, project_b, _ = await _mk_project_env(db, user)
    auth = await _guest_auth(db, project_a, user)
    with pytest.raises(AppError) as exc:
        await portal_svc.get_client_principal(db, project_b.id, auth)
    assert exc.value.code == "PROJECT_NOT_FOUND" and exc.value.status_code == 404


@pytest.mark.asyncio
async def test_guest_token_rejected_by_product_auth(db):
    """client_guest tokens must be 401 on EVERY product endpoint."""
    user = await _mk_user(db)
    _, _, _, project, _ = await _mk_project_env(db, user)
    auth = await _guest_auth(db, project, user)
    import jwt as _jwt
    from fastapi import HTTPException

    from app.api.deps import get_current_user
    from app.config import settings as app_settings

    token = auth[7:]
    payload = _jwt.decode(token, app_settings.jwt_secret, algorithms=["HS256"])
    assert payload["type"] == "client_guest"
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token, db)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_member_channel_and_role_gate(db):
    user = await _mk_user(db)
    client_user = await _mk_user(db)
    _, _, _, project, _ = await _mk_project_env(db, user)
    db.add(
        ClientPortalMember(
            project_id=project.id,
            user_id=client_user.id,
            role="reviewer",
            invited_by=user.id,
        )
    )
    await db.flush()
    auth = f"Bearer {create_access_token(client_user.id, client_user.email, 'student')}"
    principal = await portal_svc.get_client_principal(db, project.id, auth)
    assert principal.kind == "member" and principal.role == "reviewer"
    # reviewer cannot approve
    with pytest.raises(AppError) as exc:
        portal_svc.require_role(principal, "approver")
    assert exc.value.code == "CLIENT_ACCESS_DENIED"
    # Non-member user → uniform 404
    outsider = await _mk_user(db)
    auth2 = f"Bearer {create_access_token(outsider.id, outsider.email, 'student')}"
    with pytest.raises(AppError) as exc2:
        await portal_svc.get_client_principal(db, project.id, auth2)
    assert exc2.value.code == "PROJECT_NOT_FOUND"


# ── Review flow ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_full_review_flow(db):
    user = await _mk_user(db)
    org, tenant, brief, project, submission = await _mk_project_env(db, user)
    db.add(ClientShare(project_id=project.id, submission_id=submission.id, shared_by=user.id))
    await db.flush()
    auth = await _guest_auth(db, project, user, role="approver")
    principal = await portal_svc.get_client_principal(db, project.id, auth)

    # revision → submission flips + record appended
    record = await portal_svc.request_revision(
        db, principal, submission.id, "Logo too small on the hero frame"
    )
    assert record.action == "revision_requested"
    await db.refresh(submission)
    assert submission.status == SubmissionStatus.REVISION_REQUESTED

    # creator resubmits (v2 semantics: same row back to SUBMITTED here)
    submission.status = SubmissionStatus.SUBMITTED
    submission.version = 2
    await db.flush()

    approved = await portal_svc.approve(db, principal, submission.id, "Looks great")
    assert approved.action == "approved" and approved.version == 2

    final = await portal_svc.final_accept(db, principal, submission.id, "Ship it")
    assert final.action == "final_accepted"
    await db.refresh(brief)
    assert brief.status == BriefStatus.COMPLETED

    # Second final acceptance → 409 (partial unique)
    with pytest.raises(AppError) as exc:
        await portal_svc.final_accept(db, principal, submission.id, "again")
    assert exc.value.code == "FINAL_ACCEPT_CONFLICT"
    # Post-final revision blocked too
    with pytest.raises(AppError):
        await portal_svc.request_revision(db, principal, submission.id, "more changes")


@pytest.mark.asyncio
async def test_unshared_submission_uniform_404(db):
    user = await _mk_user(db)
    _, _, _, project, submission = await _mk_project_env(db, user)
    auth = await _guest_auth(db, project, user)
    principal = await portal_svc.get_client_principal(db, project.id, auth)
    # NOT shared → 404 (existence hidden)
    with pytest.raises(AppError) as exc:
        await portal_svc.assert_shared(db, project.id, submission.id)
    assert exc.value.code == "SUBMISSION_NOT_SHARED"
    with pytest.raises(AppError):
        await portal_svc.request_revision(db, principal, submission.id, "sneaky")


@pytest.mark.asyncio
async def test_internal_comments_hidden_from_portal(db):
    """Isolation: client_visible=false rows never reach portal queries."""
    user = await _mk_user(db)
    org, _, _, project, submission = await _mk_project_env(db, user)
    from app.models.project import DeliverableType, ItemType, ProjectDeliverable

    deliverable = ProjectDeliverable(project_id=project.id, name="Hero", type=DeliverableType.TEXT)
    db.add(deliverable)
    await db.flush()
    item = SubmissionItem(
        submission_id=submission.id,
        deliverable_id=deliverable.id,
        type=ItemType.TEXT,
        content="v1 text",
        uploaded_by=user.id,
    )
    db.add(item)
    await db.flush()
    internal = SubmissionComment(
        org_id=org.id,
        submission_id=submission.id,
        item_id=item.id,
        author_id=user.id,
        text="INTERNAL: client is difficult, low-ball the effort",
        client_visible=False,
    )
    visible = SubmissionComment(
        org_id=org.id,
        submission_id=submission.id,
        item_id=item.id,
        author_id=user.id,
        text="We updated the colors per your note",
        client_visible=True,
    )
    db.add_all([internal, visible])
    await db.flush()
    rows = (
        (
            await db.execute(
                select(SubmissionComment).where(
                    SubmissionComment.submission_id == submission.id,
                    SubmissionComment.client_visible.is_(True),
                )
            )
        )
        .scalars()
        .all()
    )
    texts = [c.text for c in rows]
    assert visible.text in texts
    assert all("INTERNAL" not in t for t in texts)


def test_client_brief_whitelist_excludes_sensitive_fields():
    """Static: the endpoint whitelist must never include hidden fields."""
    from app.controlplane.api.client_portal import CLIENT_BRIEF_FIELDS

    for hidden in ("budget_range", "brand_guidelines", "constraints", "created_by", "status"):
        assert hidden not in CLIENT_BRIEF_FIELDS


@pytest.mark.asyncio
async def test_portal_disabled_when_entitlement_off(db):
    user = await _mk_user(db)
    org, tenant, _, project, _ = await _mk_project_env(db, user)
    # Drop the entitlement override → community default (portal off)
    override = (
        await db.execute(
            select(TenantEntitlementOverride).where(
                TenantEntitlementOverride.tenant_id == tenant.id,
                TenantEntitlementOverride.key == "client_portal",
            )
        )
    ).scalar_one()
    await db.delete(override)
    await db.flush()
    await invalidate_cache(tenant.id)
    with pytest.raises(AppError) as exc:
        await portal_svc.require_portal_enabled(db, project)
    assert exc.value.code == "PORTAL_NOT_ENABLED"


@pytest.mark.asyncio
async def test_user_delete_nulls_comment_authorship(db):
    """R50[45]: the DB FK on submission_comments.author_id was created with NO
    ACTION while the model declares SET NULL — deleting a user with comments
    raised an FK violation. cp14 recreates the FK; deleting the author must
    null authorship, not error, and the comment survives."""
    from sqlalchemy import delete as sa_delete

    from app.models.project import DeliverableType, ItemType, ProjectDeliverable
    from app.models.user import User as _User

    user = await _mk_user(db)
    author = await _mk_user(db)
    org, _, _, project, submission = await _mk_project_env(db, user)
    deliverable = ProjectDeliverable(project_id=project.id, name="D", type=DeliverableType.TEXT)
    db.add(deliverable)
    await db.flush()
    item = SubmissionItem(
        submission_id=submission.id,
        deliverable_id=deliverable.id,
        type=ItemType.TEXT,
        content="t",
        uploaded_by=user.id,
    )
    db.add(item)
    await db.flush()
    comment = SubmissionComment(
        org_id=org.id,
        submission_id=submission.id,
        item_id=item.id,
        author_id=author.id,
        text="left by soon-deleted user",
    )
    db.add(comment)
    await db.flush()
    # Hard-delete the author — must not raise, comment survives author-less
    await db.execute(sa_delete(_User).where(_User.id == author.id))
    await db.flush()
    db.expire(comment)
    await db.refresh(comment)
    assert comment.author_id is None
    assert comment.text == "left by soon-deleted user"


# ── R69/R70: decision integrity + principal liveness + audit shape ──


@pytest.mark.asyncio
async def test_decisions_require_reviewable_status(db):
    """R69[1]: approve/final-accept accepted DRAFT / REVISION_REQUESTED
    submissions — final-accept then completed the whole brief off a draft
    the client never saw in reviewable form. Both now 409 on non-reviewable
    statuses; request_revision on REVISION_REQUESTED stays a no-op record."""
    user = await _mk_user(db)
    org, tenant, brief, project, submission = await _mk_project_env(db, user)
    db.add(ClientShare(project_id=project.id, submission_id=submission.id, shared_by=user.id))
    await db.flush()
    auth = await _guest_auth(db, project, user, role="approver")
    principal = await portal_svc.get_client_principal(db, project.id, auth)

    submission.status = SubmissionStatus.DRAFT
    await db.flush()
    with pytest.raises(AppError) as exc:
        await portal_svc.approve(db, principal, submission.id, "nice draft")
    assert exc.value.code == "SUBMISSION_NOT_REVIEWABLE"
    with pytest.raises(AppError) as exc:
        await portal_svc.final_accept(db, principal, submission.id, "ship the draft")
    assert exc.value.code == "SUBMISSION_NOT_REVIEWABLE"
    await db.refresh(brief)
    assert brief.status != BriefStatus.COMPLETED
    # SUBMITTED → both work
    submission.status = SubmissionStatus.SUBMITTED
    await db.flush()
    approved = await portal_svc.approve(db, principal, submission.id, "ok")
    assert approved.action == "approved"


@pytest.mark.asyncio
async def test_repeated_decision_is_idempotent_no_notification_spam(db):
    """R69[4]: every repeated identical approve inserted another append-only
    record and re-fanned org notifications. Same-version repeats now return
    the prior record."""
    from sqlalchemy import func as _f

    from app.controlplane.models.client_portal import ClientApprovalRecord

    user = await _mk_user(db)
    org, tenant, brief, project, submission = await _mk_project_env(db, user)
    db.add(ClientShare(project_id=project.id, submission_id=submission.id, shared_by=user.id))
    await db.flush()
    auth = await _guest_auth(db, project, user, role="approver")
    principal = await portal_svc.get_client_principal(db, project.id, auth)

    first = await portal_svc.approve(db, principal, submission.id, "great")
    again = await portal_svc.approve(db, principal, submission.id, "great again")
    assert again.id == first.id  # prior record returned, nothing inserted
    n = (
        await db.execute(
            select(_f.count(ClientApprovalRecord.id)).where(
                ClientApprovalRecord.submission_id == submission.id,
                ClientApprovalRecord.action == "approved",
            )
        )
    ).scalar_one()
    assert n == 1


@pytest.mark.asyncio
async def test_deactivated_member_loses_portal_access(db):
    """R69[2]: the member principal skipped user.is_active — a deactivated/
    banned account kept full client access for the token lifetime."""
    from app.models.user import UserStatus as ClientUserStatus

    user = await _mk_user(db)
    client_user = await _mk_user(db)
    _, _, _, project, _ = await _mk_project_env(db, user)
    db.add(
        ClientPortalMember(
            project_id=project.id,
            user_id=client_user.id,
            role="reviewer",
            invited_by=user.id,
        )
    )
    await db.flush()
    auth = f"Bearer {create_access_token(client_user.id, client_user.email, 'student')}"
    principal = await portal_svc.get_client_principal(db, project.id, auth)
    assert principal.kind == "member"
    client_user.status = ClientUserStatus.SUSPENDED
    await db.flush()
    with pytest.raises(AppError) as exc:
        await portal_svc.get_client_principal(db, project.id, auth)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_void_final_acceptance_unwedges_review_flow(db):
    """R69[3]: a final acceptance wedged the client review flow project-wide
    forever (every later decision 409s) with no recovery. Org staff can now
    void it — history preserved as final_accept_voided — and decisions
    resume."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.controlplane.models.client_portal import ClientApprovalRecord
    from app.main import app

    user = await _mk_user(db)
    org, tenant, brief, project, submission = await _mk_project_env(db, user)
    db.add(ClientShare(project_id=project.id, submission_id=submission.id, shared_by=user.id))
    await db.flush()
    auth = await _guest_auth(db, project, user, role="approver")
    principal = await portal_svc.get_client_principal(db, project.id, auth)
    final = await portal_svc.final_accept(db, principal, submission.id, "done")
    assert final.action == "final_accepted"
    with pytest.raises(AppError):
        await portal_svc.request_revision(db, principal, submission.id, "wait, no")
    # capture ids BEFORE commit expires the ORM objects
    final_id = final.id
    submission_id = submission.id
    org_id, project_id = org.id, project.id
    token = create_access_token(user.id, user.email, user.role.value)
    await db.commit()

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post(
                f"/api/v1/orgs/{org_id}/projects/{project_id}/client-approvals/void-final",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert r.status_code == 200, r.text
            assert r.json()["data"]["action"] == "final_accept_voided"
    finally:
        app.router.lifespan_context = orig
    db.expire_all()
    # history preserved, flow unwedged
    rec = await db.get(ClientApprovalRecord, final_id)
    assert rec.action == "final_accept_voided"
    submission2 = await db.get(Submission, submission_id)
    submission2.status = SubmissionStatus.SUBMITTED
    await db.flush()
    record = await portal_svc.request_revision(db, principal, submission_id, "resume")
    assert record.action == "revision_requested"


@pytest.mark.asyncio
async def test_tenant_audit_endpoint_flattens_jsonb(db):
    """R70[2]: before/after JSONB echoed verbatim to tenant members — nested
    platform-written payloads leaked internals. The endpoint now flattens to
    one level of short scalars."""
    from app.controlplane.api.tenants import _scalar_summary

    nested = {
        "plain": "ok",
        "long": "x" * 500,
        "n": 42,
        "flag": True,
        "nested": {"secret_ref": "internal"},
        "arr": [1, 2, 3],
    }
    out = _scalar_summary(nested)
    assert out["plain"] == "ok"
    assert len(out["long"]) == 200
    assert out["n"] == 42 and out["flag"] is True
    assert out["nested"] == "[…]"
    assert out["arr"] == "[…]"
    assert _scalar_summary(None) is None


@pytest.mark.asyncio
async def test_void_final_rewinds_brief_only_when_acceptance_completed_it(db):
    """R133[F13]/R134[F1]: void-final rewinds the brief COMPLETED→REVIEW only
    when THIS acceptance performed the transition — a brief the org completed
    deliberately beforehand stays COMPLETED."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.main import app
    from app.models.client_brief import BriefStatus, ClientBrief

    # Case A: acceptance completes the brief → void rewinds it.
    user = await _mk_user(db)
    org, tenant, brief, project, submission = await _mk_project_env(db, user)
    db.add(ClientShare(project_id=project.id, submission_id=submission.id, shared_by=user.id))
    await db.flush()
    auth = await _guest_auth(db, project, user, role="approver")
    principal = await portal_svc.get_client_principal(db, project.id, auth)
    final = await portal_svc.final_accept(db, principal, submission.id, "done")
    assert final.completed_brief is True
    brief_row = await db.get(ClientBrief, brief.id)
    assert brief_row.status == BriefStatus.COMPLETED
    org_id, project_id, brief_id = org.id, project.id, brief.id
    token = create_access_token(user.id, user.email, user.role.value)
    await db.commit()

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post(
                f"/api/v1/orgs/{org_id}/projects/{project_id}/client-approvals/void-final",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert r.status_code == 200, r.text
    finally:
        app.router.lifespan_context = orig
    db.expire_all()
    rewound = await db.get(ClientBrief, brief_id)
    assert rewound.status == BriefStatus.REVIEW, "acceptance-completed brief must rewind"

    # Case B: org completed the brief BEFORE the acceptance → void leaves it.
    user2 = await _mk_user(db)
    org2, tenant2, brief2, project2, submission2 = await _mk_project_env(db, user2)
    db.add(ClientShare(project_id=project2.id, submission_id=submission2.id, shared_by=user2.id))
    # Org deliberately completes the brief first.
    b2 = await db.get(ClientBrief, brief2.id)
    b2.status = BriefStatus.COMPLETED
    await db.flush()
    auth2 = await _guest_auth(db, project2, user2, role="approver")
    principal2 = await portal_svc.get_client_principal(db, project2.id, auth2)
    final2 = await portal_svc.final_accept(db, principal2, submission2.id, "ok")
    assert final2.completed_brief is False, "acceptance did not transition the brief"
    org2_id, project2_id, brief2_id = org2.id, project2.id, brief2.id
    token2 = create_access_token(user2.id, user2.email, user2.role.value)
    await db.commit()
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post(
                f"/api/v1/orgs/{org2_id}/projects/{project2_id}/client-approvals/void-final",
                headers={"Authorization": f"Bearer {token2}"},
            )
            assert r.status_code == 200, r.text
    finally:
        app.router.lifespan_context = orig
    db.expire_all()
    untouched = await db.get(ClientBrief, brief2_id)
    assert untouched.status == BriefStatus.COMPLETED, (
        "a brief the org completed deliberately must survive the void"
    )


@pytest.mark.asyncio
async def test_final_accept_recheck_under_lock_toctou():
    """R137: every portal decision path checked _assert_decidable on a
    PRE-lock read — a final-accept whose session loaded the submission as
    SUBMITTED before a concurrent revision flip committed then completed the
    brief off stale state. Two sessions: A resolves the principal and loads,
    B flips the submission to REVISION_REQUESTED and commits, A final-accepts
    with its stale object → must 409 SUBMISSION_NOT_REVIEWABLE."""
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            _, _, brief, project, submission = await _mk_project_env(setup, user)
            setup.add(ClientShare(project_id=project.id, submission_id=submission.id))
            auth = await _guest_auth(setup, project, user, role="approver")
            await setup.commit()
            project_id, submission_id, brief_id = project.id, submission.id, brief.id

        async with AsyncSessionLocal() as sa, AsyncSessionLocal() as sb:
            # A resolves the principal and (inside final_accept) will load the
            # submission — force the stale read NOW.
            principal = await portal_svc.get_client_principal(sa, project_id, auth)
            stale = await sa.get(Submission, submission_id)
            assert stale.status == SubmissionStatus.SUBMITTED
            # B: creator pulls the work back into revision and COMMITS.
            sub_b = await sb.get(Submission, submission_id)
            sub_b.status = SubmissionStatus.REVISION_REQUESTED
            await sb.commit()
            # A final-accepts off its stale SUBMITTED read → locked re-check
            # must reject.
            with pytest.raises(AppError) as exc:
                await portal_svc.final_accept(sa, principal, submission_id, "ship it")
            assert exc.value.code == "SUBMISSION_NOT_REVIEWABLE"
            await sa.rollback()

        async with AsyncSessionLocal() as s:
            b = await s.get(ClientBrief, brief_id)
            assert b.status != BriefStatus.COMPLETED, (
                "brief completed off a submission that was back in revision"
            )
    finally:
        await engine.dispose()


# ── R238: guest-link + require_role validation coverage ──


def test_require_role_pure():
    from app.controlplane.services.client_portal import ClientPrincipal, require_role
    from app.exceptions import AppError

    p = ClientPrincipal(kind="guest", role="reviewer", label="x", project_id="pr")
    require_role(p, "reviewer", "approver")   # allowed → no raise
    with pytest.raises(AppError) as e:
        require_role(p, "approver")           # reviewer lacks approver
    assert e.value.code == "CLIENT_ACCESS_DENIED"


@pytest.mark.asyncio
async def test_create_guest_link_validation(db):
    from datetime import UTC, datetime, timedelta

    user = await _mk_user(db)
    _, _, _, project, _ = await _mk_project_env(db, user)

    async def rejects(**kw):
        base = dict(project_id=project.id, label=None, email=None, role="approver",
                    expires_at=datetime.now(UTC) + timedelta(days=7), actor=_actor(user))
        base.update(kw)
        with pytest.raises(AppError) as e:
            await portal_svc.create_guest_link(db, **base)
        assert e.value.code == "VALIDATION_ERROR"

    await rejects(role="editor")                                       # bad role
    await rejects(expires_at=datetime.now(UTC) - timedelta(days=1))    # already expired
    await rejects(expires_at=datetime.now(UTC) + timedelta(days=91))   # >90 days


# ── R269: remaining portal arcs ──


@pytest.mark.asyncio
async def test_link_limit_and_auth_arcs(db):
    """R269: the 20-active-links project cap, malformed/missing Bearer 401s,
    the impersonation block (an impersonated admin session must NOT act as a
    client — decisions would be recorded under the impersonated identity)."""
    user = await _mk_user(db)
    _, _, _, project, _ = await _mk_project_env(db, user)

    async def mk_link():
        return await portal_svc.create_guest_link(
            db, project_id=project.id, label="L", email=None, role="reviewer",
            expires_at=datetime.now(UTC) + timedelta(days=7), actor=_actor(user))

    for _ in range(portal_svc.MAX_ACTIVE_LINKS_PER_PROJECT):
        await mk_link()
    with pytest.raises(AppError) as e:                    # 21st link
        await mk_link()
    assert e.value.code == "CLIENT_LINK_LIMIT" and e.value.status_code == 422

    # auth arcs
    with pytest.raises(AppError) as e:
        await portal_svc.get_client_principal(db, project.id, None)
    assert e.value.status_code == 401
    with pytest.raises(AppError) as e:
        await portal_svc.get_client_principal(db, project.id, "Basic abc")
    assert e.value.status_code == 401
    with pytest.raises(AppError) as e:
        await portal_svc.get_client_principal(db, project.id, "Bearer not-a-jwt")
    assert e.value.status_code == 401

    # an impersonated platform-access token is refused as a client principal
    import jwt as _jwt

    from app.config import settings as _settings
    from app.core.security import ALGORITHM, create_access_token

    token = create_access_token(user.id, user.email, "admin")
    payload = _jwt.decode(token, _settings.jwt_secret, algorithms=[ALGORITHM])
    payload["imp"] = "someone-else"
    imp_token = _jwt.encode(payload, _settings.jwt_secret, algorithm=ALGORITHM)
    with pytest.raises(AppError) as e:
        await portal_svc.get_client_principal(db, project.id, f"Bearer {imp_token}")
    assert e.value.code == "IMPERSONATION_FORBIDDEN" and e.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_project_submission_404_and_revision_replay(db):
    """R269: a submission id from ANOTHER project is a uniform 404 through
    the portal share gate, and a replayed revision-request returns the prior
    decision replay 409s without double-recording."""
    from app.controlplane.models.client_portal import ClientApprovalRecord

    user = await _mk_user(db)
    _, _, _, project, submission = await _mk_project_env(db, user)
    _, _, _, project2, submission2 = await _mk_project_env(db, user)
    auth = await _guest_auth(db, project, user, role="approver")
    principal = await portal_svc.get_client_principal(db, project.id, auth)
    db.add(ClientShare(project_id=project.id, submission_id=submission.id, shared_by=user.id))
    # share submission2 in ITS project — the cross-project probe must still 404
    db.add(ClientShare(project_id=project2.id, submission_id=submission2.id, shared_by=user.id))
    await db.flush()

    with pytest.raises(AppError) as e:                    # other project's submission
        await portal_svc.assert_shared(db, project.id, submission2.id)
    assert e.value.code == "SUBMISSION_NOT_SHARED" and e.value.status_code == 404

    d1 = await portal_svc.request_revision(db, principal, submission.id, "colors off")
    assert d1 is not None
    with pytest.raises(AppError) as e:                    # replay: status already
        await portal_svc.request_revision(db, principal, submission.id, "again?")
    assert e.value.code == "SUBMISSION_NOT_REVIEWABLE" and e.value.status_code == 409
    records = (
        (await db.execute(
            select(ClientApprovalRecord).where(
                ClientApprovalRecord.submission_id == submission.id,
                ClientApprovalRecord.action == "revision_requested")))
        .scalars().all()
    )
    assert len(records) == 1                              # never double-recorded


@pytest.mark.asyncio
async def test_every_portal_route_rejects_foreign_project_guest(db):
    """R280: portal cross-project sweep (fourth member of the R277-R279
    tripwire family). A guest of project A hitting EVERY
    /client-portal/projects/{project_id} route with project B's REAL id gets
    uniform 401/403/404 — never 2xx (cross-client leak of briefs,
    submissions, comments, downloads) and never 500. Enumerated from the
    live route table, so future portal routes are covered the day they land."""
    import re as _re

    from fastapi.routing import APIRoute
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    user = await _mk_user(db)
    _, _, _, project_a, _ = await _mk_project_env(db, user)
    _, _, _, project_b, submission_b = await _mk_project_env(db, user)
    auth_a = await _guest_auth(db, project_a, user, role="approver")
    await db.commit()  # the ASGI app reads through its own sessions

    routes = []

    def walk(r):
        if isinstance(r, APIRoute):
            path = "/api/v1" + r.path
            if path.startswith("/api/v1/client-portal/projects/{project_id}"):
                concrete = path.replace("{project_id}", project_b.id)
                concrete = concrete.replace("{submission_id}", submission_b.id)
                concrete = _re.sub(r"\{[^}]+\}", "01JFAKEFAKEFAKEFAKEFAKEFAK", concrete)
                for m in sorted(r.methods - {"HEAD", "OPTIONS"}):
                    routes.append((m, concrete))
        for sub in getattr(r, "routes", []) or []:
            walk(sub)
        orig = getattr(r, "original_router", None)
        if orig is not None:
            walk(orig)

    for r in app.routes:
        walk(r)
    routes = sorted(set(routes))
    assert len(routes) >= 8, f"route enumeration broke: {routes}"

    offenders = []
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        for method, path in routes:
            kwargs: dict = {"headers": {"Authorization": auth_a}}
            if method in ("POST", "PUT", "PATCH"):
                kwargs["json"] = {}
            r2 = await c.request(method, path, **kwargs)
            allowed = {401, 403, 404} if method in ("GET", "DELETE") else {401, 403, 404, 422}
            if r2.status_code not in allowed:
                offenders.append((method, path, r2.status_code))
    assert offenders == [], offenders


@pytest.mark.asyncio
async def test_guest_token_never_outlives_its_link(db):
    """R305: exp = min(link.expires_at, now + token TTL). A near-expiry link
    must mint a SHORT token, never one living the full client_guest TTL — a
    2-minute link handing out a 30-minute credential would keep portal access
    alive long after the link was meant to die. Also the reciprocal: a
    long-lived link is capped at the token TTL, not the link's."""
    import jwt as _jwt

    from app.config import settings as _settings
    from app.core.security import ALGORITHM

    user = await _mk_user(db)
    _, _, _, project, _ = await _mk_project_env(db, user)
    ttl_min = _settings.client_guest_token_expire_minutes

    # link expiring in ~2 minutes — well under the token TTL
    short = await portal_svc.create_guest_link(
        db, project_id=project.id, label=None, email=None, role="reviewer",
        expires_at=datetime.now(UTC) + timedelta(minutes=2), actor=_actor(user))
    link, raw = short
    token, ctx = await portal_svc.exchange_guest_token(db, raw, None)
    # capped by the LINK, not the (larger) token TTL
    assert ctx["expires_in"] <= 2 * 60 + 5
    assert ctx["expires_in"] < ttl_min * 60
    payload = _jwt.decode(token, _settings.jwt_secret, algorithms=[ALGORITHM])
    exp_dt = datetime.fromtimestamp(payload["exp"], tz=UTC)
    assert exp_dt <= link.expires_at + timedelta(seconds=1)

    # link far in the future — token capped at the TTL, not the link
    longlink, raw2 = await portal_svc.create_guest_link(
        db, project_id=project.id, label=None, email=None, role="reviewer",
        expires_at=datetime.now(UTC) + timedelta(days=80), actor=_actor(user))
    _, ctx2 = await portal_svc.exchange_guest_token(db, raw2, None)
    assert ctx2["expires_in"] <= ttl_min * 60 + 5
    assert ctx2["expires_in"] < 80 * 24 * 3600


@pytest.mark.asyncio
async def test_reviewer_guest_cannot_approve_or_final_accept_via_http(db):
    """R318: the client-decision role gate lives in the ENDPOINTS (approve /
    final-accept require the 'approver' role; request-revision allows both).
    A REVIEWER guest token must be 403 on approve and final-accept but 200 on
    request-revision — enforced through the real HTTP layer, since removing
    the endpoint's require_role call is exactly the hole this catches."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.main import app

    user = await _mk_user(db)
    _, _, _, project, submission = await _mk_project_env(db, user)
    db.add(ClientShare(project_id=project.id, submission_id=submission.id, shared_by=user.id))
    reviewer_auth = await _guest_auth(db, project, user, role="reviewer")
    await db.commit()

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            hdr = {"Authorization": reviewer_auth}
            base = f"/api/v1/client-portal/projects/{project.id}"

            r = await c.post(f"{base}/submissions/{submission.id}/approve",
                             headers=hdr, json={"comment": "lgtm"})
            assert r.status_code == 403, r.text
            assert r.json()["error"]["code"] == "CLIENT_ACCESS_DENIED"

            r = await c.post(f"{base}/final-accept", headers=hdr,
                             json={"submission_id": submission.id, "comment": "ship"})
            assert r.status_code == 403, r.text

            # a reviewer CAN request a revision
            r = await c.post(f"{base}/submissions/{submission.id}/request-revision",
                             headers=hdr, json={"comment": "please fix the colors"})
            assert r.status_code in (200, 201), r.text
    finally:
        app.router.lifespan_context = orig
