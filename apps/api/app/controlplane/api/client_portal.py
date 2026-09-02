"""Client portal endpoints (ADR-014 §9.3–9.4).

Two surfaces:
- /client-portal/*  — the external client (guest JWT or member account);
  every response is a dedicated whitelisted shape (R82 total-fields rule).
- /orgs/{org_id}/projects/{project_id}/client-* — internal management
  (instructor+): members, guest links, shares.
"""

from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.controlplane.api.deps import make_actor
from app.controlplane.models.client_portal import (
    ClientApprovalRecord,
    ClientGuestLink,
    ClientPortalMember,
    ClientShare,
)
from app.controlplane.services import client_portal as portal_svc
from app.controlplane.services.audit import record_audit
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.organization import OrgRole
from app.models.project import (
    CommentAnchorType,
    Project,
    Submission,
    SubmissionComment,
    SubmissionItem,
)
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta, reject_ctrl_str

log = structlog.get_logger()

router = APIRouter(tags=["Client Portal"])

_STAFF_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)

# Whitelisted brief fields (issue §29: budget_range, brand_guidelines,
# constraints and internal fields are HIDDEN). Asserted by tests.
CLIENT_BRIEF_FIELDS = frozenset(
    {
        "title",
        "client_name",
        "objective",
        "target_audience",
        "deliverable_specs",
        "tone_and_style",
        "references",
        "timeline",
        "evaluation_criteria",
    }
)


class GuestSessionRequest(BaseModel):
    token: str = Field(min_length=16, max_length=128)
    email: EmailStr | None = None


class ClientCommentRequest(BaseModel):
    item_id: str = Field(min_length=26, max_length=26)
    text: str = Field(min_length=1, max_length=5000)
    anchor_type: str = Field(default="global", pattern=r"^(global|time|region)$")
    timestamp_ms: int | None = Field(default=None, ge=0)
    duration_ms: int | None = Field(default=None, ge=0)
    region: dict | None = None

    @field_validator("region")
    @classmethod
    def _region(cls, v):
        # R58[33]: a ~300-level-deep nested dict stored to JSONB poisoned the
        # whole comment thread with a persistent 500 (recursion at serialize).
        # Same guard every other JSONB field uses.
        from app.schemas.base import reject_ctrl_json, reject_deep_json

        if v is not None:
            reject_deep_json(v, "region", limit=16)
            reject_ctrl_json(v, "region")
        return v

    @field_validator("text")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class DecisionRequest(BaseModel):
    comment: str | None = Field(default=None, max_length=2000)

    @field_validator("comment")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class FinalAcceptRequest(BaseModel):
    submission_id: str = Field(min_length=26, max_length=26)
    comment: str | None = Field(default=None, max_length=2000)

    @field_validator("comment")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class AddClientMemberRequest(BaseModel):
    user_id: str = Field(min_length=26, max_length=26)
    role: str = Field(pattern=r"^(reviewer|approver)$")


class CreateGuestLinkRequest(BaseModel):
    label: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    role: str = Field(pattern=r"^(reviewer|approver)$")
    expires_at: datetime

    @field_validator("expires_at")
    @classmethod
    def _aware(cls, v):
        # R45[23]: a naive ISO datetime (no offset — the common client shape)
        # crashed the service's aware-datetime comparison with a 500. Coerce to
        # UTC like every other datetime schema in the codebase.
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v

    @field_validator("label")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class ShareRequest(BaseModel):
    submission_id: str = Field(min_length=26, max_length=26)
    note: str | None = Field(default=None, max_length=500)

    @field_validator("note")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


async def _principal(
    project_id: str,
    db: AsyncSession,
    authorization: str | None,
) -> portal_svc.ClientPrincipal:
    principal = await portal_svc.get_client_principal(db, project_id, authorization)
    project = await db.get(Project, project_id)
    if project is None:
        raise AppError("PROJECT_NOT_FOUND", "Project not found", 404)
    await portal_svc.require_portal_enabled(db, project)
    return principal


def _approval_response(r: ClientApprovalRecord) -> dict:
    return {
        "id": r.id,
        "submission_id": r.submission_id,
        "version": r.version,
        "action": r.action,
        "comment": r.comment,
        "acted_by": r.acted_by_label,
        "created_at": r.created_at.isoformat(),
    }


# ── Guest session exchange ───────────────────────────────────


@router.post("/client-portal/guest-session", dependencies=[Depends(rate_limit(10, 60))])
async def guest_session(
    body: GuestSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    token, context = await portal_svc.exchange_guest_token(db, body.token, body.email)
    await db.commit()  # use_count/last_used persisted
    return DataResponse(data={"access_token": token, "token_type": "bearer", **context})


# ── Portal (client-facing) ───────────────────────────────────


@router.get(
    "/client-portal/projects/{project_id}/brief",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def portal_brief(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    await _principal(project_id, db, authorization)
    project = await db.get(Project, project_id)
    if not project.client_brief_id:
        raise AppError("PROJECT_NOT_FOUND", "No brief for this project", 404)
    from app.models.client_brief import ClientBrief

    brief = await db.get(ClientBrief, project.client_brief_id)
    if brief is None:
        raise AppError("PROJECT_NOT_FOUND", "No brief for this project", 404)
    # WHITELIST construction — hidden: budget_range, brand_guidelines,
    # constraints, created_by, status internals (test-asserted)
    return DataResponse(
        data={
            "title": brief.title,
            "client_name": brief.client_name,
            "objective": brief.objective,
            "target_audience": brief.target_audience,
            "deliverable_specs": brief.deliverable_specs,
            "tone_and_style": brief.tone_and_style,
            "references": brief.references,
            "timeline": brief.timeline,
            "evaluation_criteria": brief.evaluation_criteria,
        }
    )


@router.get(
    "/client-portal/projects/{project_id}/submissions",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def portal_submissions(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    await _principal(project_id, db, authorization)
    rows = (
        await db.execute(
            select(Submission, ClientShare.note)
            .join(ClientShare, ClientShare.submission_id == Submission.id)
            .where(ClientShare.project_id == project_id)
            .order_by(Submission.version.desc())
        )
    ).all()
    data = []
    for submission, note in rows:
        items = (
            (
                await db.execute(
                    select(SubmissionItem).where(SubmissionItem.submission_id == submission.id)
                )
            )
            .scalars()
            .all()
        )
        data.append(
            {
                "id": submission.id,
                "version": submission.version,
                "status": submission.status.value,
                "submitted_at": (
                    submission.submitted_at.isoformat() if submission.submitted_at else None
                ),
                "share_note": note,
                "items": [
                    {
                        "id": item.id,
                        "type": item.type.value,
                        "file_name": item.file_name,
                        "mime_type": item.mime_type,
                        "content": item.content if item.type.value != "file" else None,
                        "version": item.version,
                    }
                    for item in items
                ],
            }
        )
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.get(
    "/client-portal/projects/{project_id}/submissions/{submission_id}/items/{item_id}/download",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def portal_download(
    project_id: str,
    submission_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    await _principal(project_id, db, authorization)
    await portal_svc.assert_shared(db, project_id, submission_id)
    item = await db.get(SubmissionItem, item_id)
    if item is None or item.submission_id != submission_id or not item.file_key:
        raise AppError("SUBMISSION_NOT_SHARED", "File not found", 404)
    from app.services.project import ProjectService

    svc = ProjectService(db)
    url = await svc.get_download_url(item_id, submission_id=submission_id)
    return DataResponse(data={"download_url": url})


@router.get(
    "/client-portal/projects/{project_id}/submissions/{submission_id}/comments",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def portal_list_comments(
    project_id: str,
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    await _principal(project_id, db, authorization)
    await portal_svc.assert_shared(db, project_id, submission_id)
    rows = (
        (
            await db.execute(
                select(SubmissionComment)
                .where(
                    SubmissionComment.submission_id == submission_id,
                    # Hard filter: internal comments NEVER reach the portal
                    SubmissionComment.client_visible.is_(True),
                )
                .order_by(SubmissionComment.created_at)
            )
        )
        .scalars()
        .all()
    )
    data = []
    for c in rows:
        author = c.client_author_label
        if author is None and c.author_id is not None:
            from app.models.user import User as _User

            u = await db.get(_User, c.author_id)
            author = u.display_name if u else "Team"
        data.append(
            {
                "id": c.id,
                "item_id": c.item_id,
                "text": c.text,
                "anchor_type": c.anchor_type.value,
                "timestamp_ms": c.timestamp_ms,
                "duration_ms": c.duration_ms,
                "region": c.region,
                "author": author or "Team",
                "created_at": c.created_at.isoformat(),
            }
        )
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.post(
    "/client-portal/projects/{project_id}/submissions/{submission_id}/comments",
    status_code=201,
    dependencies=[Depends(rate_limit(30, 60))],
)
async def portal_create_comment(
    project_id: str,
    submission_id: str,
    body: ClientCommentRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    principal = await _principal(project_id, db, authorization)
    submission = await portal_svc.assert_shared(db, project_id, submission_id)
    item = await db.get(SubmissionItem, body.item_id)
    if item is None or item.submission_id != submission_id:
        raise AppError("SUBMISSION_NOT_SHARED", "Item not found", 404)
    comment = SubmissionComment(
        org_id=submission.org_id,
        submission_id=submission_id,
        item_id=body.item_id,
        author_id=principal.user_id,  # None for guests
        text=body.text,
        anchor_type=CommentAnchorType(body.anchor_type),
        timestamp_ms=body.timestamp_ms,
        duration_ms=body.duration_ms,
        region=body.region,
        client_visible=True,  # forced — client comments are always visible
        client_author_label=principal.label,
    )
    db.add(comment)
    await db.commit()
    return DataResponse(data={"id": comment.id, "created_at": comment.created_at.isoformat()})


@router.post(
    "/client-portal/projects/{project_id}/submissions/{submission_id}/request-revision",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def portal_request_revision(
    project_id: str,
    submission_id: str,
    body: DecisionRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    principal = await _principal(project_id, db, authorization)
    portal_svc.require_role(principal, "reviewer", "approver")
    if not body.comment:
        raise AppError("VALIDATION_ERROR", "A revision request needs a comment", 422)
    record = await portal_svc.request_revision(db, principal, submission_id, body.comment)
    await db.commit()
    return DataResponse(data=_approval_response(record))


@router.post(
    "/client-portal/projects/{project_id}/submissions/{submission_id}/approve",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def portal_approve(
    project_id: str,
    submission_id: str,
    body: DecisionRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    principal = await _principal(project_id, db, authorization)
    portal_svc.require_role(principal, "approver")
    record = await portal_svc.approve(db, principal, submission_id, body.comment)
    await db.commit()
    return DataResponse(data=_approval_response(record))


@router.post(
    "/client-portal/projects/{project_id}/final-accept",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def portal_final_accept(
    project_id: str,
    body: FinalAcceptRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    principal = await _principal(project_id, db, authorization)
    portal_svc.require_role(principal, "approver")
    record = await portal_svc.final_accept(db, principal, body.submission_id, body.comment)
    await db.commit()
    return DataResponse(data=_approval_response(record))


@router.get(
    "/client-portal/projects/{project_id}/approval-history",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def portal_history(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    await _principal(project_id, db, authorization)
    rows = (
        (
            await db.execute(
                select(ClientApprovalRecord)
                .where(ClientApprovalRecord.project_id == project_id)
                .order_by(ClientApprovalRecord.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_approval_response(r) for r in rows],
        meta=PaginationMeta(total=len(rows), page=1, per_page=len(rows) or 1, has_more=False),
    )


# ── Internal management (org instructor+) ────────────────────


async def _staff_project(db: AsyncSession, org_id: str, project_id: str, user) -> Project:
    await require_org_member(org_id, user, db, *_STAFF_ROLES)
    project = await db.get(Project, project_id)
    if project is None or project.org_id != org_id:
        raise AppError("PROJECT_NOT_FOUND", "Project not found", 404)
    return project


@router.get(
    "/orgs/{org_id}/projects/{project_id}/client-members",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_client_members(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _staff_project(db, org_id, project_id, user)
    rows = (
        (
            await db.execute(
                select(ClientPortalMember).where(ClientPortalMember.project_id == project_id)
            )
        )
        .scalars()
        .all()
    )
    data = [{"id": m.id, "user_id": m.user_id, "role": m.role, "status": m.status} for m in rows]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.post(
    "/orgs/{org_id}/projects/{project_id}/client-members",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def add_client_member(
    org_id: str,
    project_id: str,
    body: AddClientMemberRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _staff_project(db, org_id, project_id, user)
    await portal_svc.require_portal_enabled(db, project)
    target = await db.get(User, body.user_id)
    if target is None:
        raise AppError("USER_NOT_FOUND", "User not found", 404)
    dup = (
        await db.execute(
            select(ClientPortalMember).where(
                ClientPortalMember.project_id == project_id,
                ClientPortalMember.user_id == body.user_id,
            )
        )
    ).scalar_one_or_none()
    if dup is not None:
        if dup.status == "revoked":
            dup.status = "active"
            dup.role = body.role
            await db.commit()
            return DataResponse(data={"id": dup.id, "role": dup.role})
        raise AppError("VALIDATION_ERROR", "Already a portal member", 409)
    member = ClientPortalMember(
        project_id=project_id, user_id=body.user_id, role=body.role, invited_by=user.id
    )
    db.add(member)
    await db.commit()
    return DataResponse(data={"id": member.id, "role": member.role})


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/client-members/{member_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def revoke_client_member(
    org_id: str,
    project_id: str,
    member_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _staff_project(db, org_id, project_id, user)
    member = await db.get(ClientPortalMember, member_id)
    if member is None or member.project_id != project_id:
        raise AppError("PROJECT_NOT_FOUND", "Member not found", 404)
    member.status = "revoked"
    await db.commit()


@router.get(
    "/orgs/{org_id}/projects/{project_id}/client-links",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_guest_links(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _staff_project(db, org_id, project_id, user)
    rows = (
        (
            await db.execute(
                select(ClientGuestLink)
                .where(ClientGuestLink.project_id == project_id)
                .order_by(ClientGuestLink.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    # token_hash intentionally excluded
    data = [
        {
            "id": link.id,
            "label": link.label,
            "email": link.email,
            "role": link.role,
            "expires_at": link.expires_at.isoformat(),
            "revoked_at": link.revoked_at.isoformat() if link.revoked_at else None,
            "use_count": link.use_count,
            "last_used_at": link.last_used_at.isoformat() if link.last_used_at else None,
        }
        for link in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.post(
    "/orgs/{org_id}/projects/{project_id}/client-links",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_guest_link(
    org_id: str,
    project_id: str,
    body: CreateGuestLinkRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _staff_project(db, org_id, project_id, user)
    await portal_svc.require_portal_enabled(db, project)
    from app.controlplane import facade

    tenant = await facade.get_tenant_for_org(db, org_id)
    facade.require_tenant_active(tenant)
    link, raw_token = await portal_svc.create_guest_link(
        db,
        project_id=project_id,
        label=body.label,
        email=body.email,
        role=body.role,
        expires_at=body.expires_at,
        actor=make_actor(request, user, "tenant"),
    )
    await db.commit()
    # Raw token in THIS response only — never retrievable again
    return DataResponse(
        data={
            "id": link.id,
            "token": raw_token,
            "role": link.role,
            "expires_at": link.expires_at.isoformat(),
        }
    )


@router.post(
    "/orgs/{org_id}/projects/{project_id}/client-links/{link_id}/revoke",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def revoke_guest_link(
    org_id: str,
    project_id: str,
    link_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import UTC

    await _staff_project(db, org_id, project_id, user)
    link = await db.get(ClientGuestLink, link_id)
    if link is None or link.project_id != project_id:
        raise AppError("PROJECT_NOT_FOUND", "Link not found", 404)
    if link.revoked_at is None:
        link.revoked_at = datetime.now(UTC)
        await record_audit(
            db,
            actor=make_actor(request, user, "tenant"),
            action="client_link.revoked",
            target_type="client_guest_link",
            target_id=link.id,
        )
    await db.commit()
    return DataResponse(data={"id": link.id, "revoked": True})


@router.get(
    "/orgs/{org_id}/projects/{project_id}/client-shares",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_shares(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _staff_project(db, org_id, project_id, user)
    rows = (
        (await db.execute(select(ClientShare).where(ClientShare.project_id == project_id)))
        .scalars()
        .all()
    )
    data = [{"id": s.id, "submission_id": s.submission_id, "note": s.note} for s in rows]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.post(
    "/orgs/{org_id}/projects/{project_id}/client-shares",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def share_submission(
    org_id: str,
    project_id: str,
    body: ShareRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _staff_project(db, org_id, project_id, user)
    submission = await db.get(Submission, body.submission_id)
    if submission is None or submission.project_id != project_id:
        raise AppError("VALIDATION_ERROR", "Submission does not belong to this project", 422)
    dup = (
        await db.execute(select(ClientShare).where(ClientShare.submission_id == body.submission_id))
    ).scalar_one_or_none()
    if dup is not None:
        raise AppError("VALIDATION_ERROR", "Submission already shared", 409)
    share = ClientShare(
        project_id=project_id,
        submission_id=body.submission_id,
        shared_by=user.id,
        note=body.note,
    )
    db.add(share)
    await db.commit()
    return DataResponse(data={"id": share.id, "submission_id": share.submission_id})


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/client-shares/{share_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def unshare_submission(
    org_id: str,
    project_id: str,
    share_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _staff_project(db, org_id, project_id, user)
    share = await db.get(ClientShare, share_id)
    if share is None or share.project_id != project_id:
        raise AppError("PROJECT_NOT_FOUND", "Share not found", 404)
    await db.delete(share)
    await db.commit()


@router.post(
    "/orgs/{org_id}/projects/{project_id}/client-approvals/void-final",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def void_final_acceptance(
    org_id: str,
    project_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """R69[3]: a final acceptance permanently wedged the project's client
    review flow — unshare, new versions, everything after it 409'd on
    _assert_no_final with no recovery path. Org staff can void it (audited);
    the partial unique index frees up and the review flow resumes. The
    decision history is preserved: the record's action flips to
    'final_accept_voided', it is never deleted."""
    from sqlalchemy import update as _sa_update

    from app.controlplane.models.client_portal import ClientApprovalRecord

    await _staff_project(db, org_id, project_id, user)
    result = await db.execute(
        _sa_update(ClientApprovalRecord)
        .where(
            ClientApprovalRecord.project_id == project_id,
            ClientApprovalRecord.action == "final_accepted",
        )
        .values(action="final_accept_voided")
        .returning(ClientApprovalRecord.id)
    )
    voided_id = result.scalar_one_or_none()
    if voided_id is None:
        raise AppError("PROJECT_NOT_FOUND", "No final acceptance to void", 404)
    import contextlib

    tenant = None
    from app.controlplane.services.tenants import get_tenant_for_org

    with contextlib.suppress(AppError):
        tenant = await get_tenant_for_org(db, org_id)
    await record_audit(
        db,
        actor=make_actor(request, user, "tenant"),
        action="client_approval.final_voided",
        target_type="client_approval",
        target_id=voided_id,
        tenant_id=tenant.id if tenant else None,
        after={"project_id": project_id},
    )
    await db.commit()
    return {"data": {"id": voided_id, "action": "final_accept_voided"}}
