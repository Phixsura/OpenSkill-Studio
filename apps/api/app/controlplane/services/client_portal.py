"""Client portal: guest sessions, principals, review flow (ADR-014 §9)."""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.controlplane.models.client_portal import (
    ClientApprovalRecord,
    ClientGuestLink,
    ClientPortalMember,
    ClientShare,
)
from app.controlplane.services.audit import Actor, record_audit
from app.core.security import ALGORITHM
from app.exceptions import AppError
from app.models.project import Project, Submission, SubmissionStatus

log = structlog.get_logger()

MAX_ACTIVE_LINKS_PER_PROJECT = 20


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class ClientPrincipal:
    kind: str  # guest | member
    role: str  # reviewer | approver
    label: str
    project_id: str
    link_id: str | None = None
    user_id: str | None = None


# ── Guest links ──────────────────────────────────────────────


async def create_guest_link(
    db: AsyncSession,
    *,
    project_id: str,
    label: str | None,
    email: str | None,
    role: str,
    expires_at: datetime,
    actor: Actor,
) -> tuple[ClientGuestLink, str]:
    """Returns (link, RAW token) — the raw token is shown exactly once."""
    if role not in ("reviewer", "approver"):
        raise AppError("VALIDATION_ERROR", "role must be reviewer|approver", 422)
    if expires_at <= _now() or expires_at > _now() + timedelta(days=90):
        raise AppError("VALIDATION_ERROR", "expires_at must be within 90 days", 422)
    active_count = (
        await db.execute(
            select(func.count(ClientGuestLink.id)).where(
                ClientGuestLink.project_id == project_id,
                ClientGuestLink.revoked_at.is_(None),
                ClientGuestLink.expires_at > _now(),
            )
        )
    ).scalar_one()
    if active_count >= MAX_ACTIVE_LINKS_PER_PROJECT:
        raise AppError(
            "CLIENT_LINK_LIMIT",
            f"A project may have at most {MAX_ACTIVE_LINKS_PER_PROJECT} active links",
            422,
        )
    raw_token = secrets.token_urlsafe(32)
    link = ClientGuestLink(
        project_id=project_id,
        token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
        label=label,
        email=email.lower() if email else None,
        role=role,
        expires_at=expires_at,
        created_by=actor.user_id,
    )
    db.add(link)
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="client_link.created",
        target_type="client_guest_link",
        target_id=link.id,
        after={"project_id": project_id, "role": role, "label": label},
        # raw token NEVER audited/logged
    )
    return link, raw_token


async def exchange_guest_token(
    db: AsyncSession, raw_token: str, email: str | None
) -> tuple[str, dict]:
    """Token → short-lived client_guest JWT. Uniform 401 on every failure
    mode (missing/expired/revoked/email mismatch) — no enumeration."""
    invalid = AppError("GUEST_LINK_INVALID", "This link is invalid or has expired", 401)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    link = (
        await db.execute(select(ClientGuestLink).where(ClientGuestLink.token_hash == token_hash))
    ).scalar_one_or_none()
    if link is None or link.revoked_at is not None or link.expires_at <= _now():
        raise invalid
    if link.email is not None and (email or "").lower() != link.email:
        raise invalid
    link.use_count += 1
    link.last_used_at = _now()
    project = await db.get(Project, link.project_id)
    if project is None:
        raise invalid
    exp = min(
        link.expires_at,
        _now() + timedelta(minutes=settings.client_guest_token_expire_minutes),
    )
    from ulid import ULID

    payload = {
        "sub": link.id,
        "type": "client_guest",
        "project_id": link.project_id,
        "role": link.role,
        "iat": _now(),
        "exp": exp,
        "jti": str(ULID()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
    return token, {
        "project": {"id": project.id, "title": project.title},
        "role": link.role,
        "label": link.label,
        "expires_in": int((exp - _now()).total_seconds()),
    }


async def get_client_principal(
    db: AsyncSession, project_id: str, authorization: str | None
) -> ClientPrincipal:
    """Resolve guest OR member principal for a project. Revocation is
    re-checked EVERY request; anything else → uniform 404/403."""
    not_found = AppError("PROJECT_NOT_FOUND", "Project not found", 404)
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError("CLIENT_ACCESS_DENIED", "Authentication required", 401)
    token = authorization[7:]
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except Exception as exc:  # noqa: BLE001
        raise AppError("CLIENT_ACCESS_DENIED", "Invalid or expired token", 401) from exc

    if payload.get("type") == "client_guest":
        if payload.get("project_id") != project_id:
            raise not_found  # cross-project token → uniform 404
        link = await db.get(ClientGuestLink, payload.get("sub", ""))
        if link is None or link.revoked_at is not None or link.expires_at <= _now():
            # 401, not 403: a revoked/expired link is a dead credential (same
            # class as an expired token) — the portal UI bounces 401s back to
            # the access page, while 403 is reserved for live sessions hitting
            # a role gate and must NOT end the session.
            raise AppError("CLIENT_ACCESS_DENIED", "Access has been revoked", 401)
        return ClientPrincipal(
            kind="guest",
            role=link.role,
            label=link.label or "Client reviewer",
            project_id=project_id,
            link_id=link.id,
        )

    if payload.get("type") == "access":
        if "imp" in payload:
            raise AppError(
                "IMPERSONATION_FORBIDDEN", "Impersonated sessions cannot act as clients", 403
            )
        user_id = payload.get("sub")
        member = (
            await db.execute(
                select(ClientPortalMember).where(
                    ClientPortalMember.project_id == project_id,
                    ClientPortalMember.user_id == (user_id or ""),
                    ClientPortalMember.status == "active",
                )
            )
        ).scalar_one_or_none()
        if member is None:
            raise not_found  # non-member → uniform 404
        from app.models.user import User

        user = await db.get(User, user_id)
        # R69[2]: the portal re-implements token handling and dropped the
        # user liveness check get_current_user enforces — a deactivated/
        # deleted account kept full client access for the token's lifetime.
        if user is None or not user.is_active:
            raise AppError("CLIENT_ACCESS_DENIED", "Account is not active", 401)
        return ClientPrincipal(
            kind="member",
            role=member.role,
            label=user.display_name,
            project_id=project_id,
            user_id=user_id,
        )
    raise AppError("CLIENT_ACCESS_DENIED", "Invalid token type", 401)


def require_role(principal: ClientPrincipal, *roles: str) -> None:
    if principal.role not in roles:
        raise AppError("CLIENT_ACCESS_DENIED", "Insufficient portal permissions", 403)


# ── Portal gating (entitlement + tenant status) ──────────────


async def require_portal_enabled(db: AsyncSession, project: Project) -> None:
    from app.controlplane.services.entitlements import get_effective
    from app.controlplane.services.tenants import get_tenant_for_org

    tenant = await get_tenant_for_org(db, project.org_id)
    eff = await get_effective(db, tenant)
    if not eff.values.get("client_portal"):
        raise AppError("PORTAL_NOT_ENABLED", "Client portal is not enabled for this account", 403)


# ── Review flow ──────────────────────────────────────────────


async def assert_shared(db: AsyncSession, project_id: str, submission_id: str) -> Submission:
    share = (
        await db.execute(
            select(ClientShare).where(
                ClientShare.project_id == project_id,
                ClientShare.submission_id == submission_id,
            )
        )
    ).scalar_one_or_none()
    if share is None:
        raise AppError("SUBMISSION_NOT_SHARED", "Submission not found", 404)
    submission = await db.get(Submission, submission_id)
    if submission is None or submission.project_id != project_id:
        raise AppError("SUBMISSION_NOT_SHARED", "Submission not found", 404)
    return submission


async def _assert_no_final(db: AsyncSession, project_id: str) -> None:
    final = (
        await db.execute(
            select(ClientApprovalRecord.id)
            .where(
                ClientApprovalRecord.project_id == project_id,
                ClientApprovalRecord.action == "final_accepted",
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if final is not None:
        raise AppError("FINAL_ACCEPT_CONFLICT", "Project already has a final acceptance", 409)


def _record(principal: ClientPrincipal, submission: Submission, action: str, comment: str | None):
    return ClientApprovalRecord(
        project_id=principal.project_id,
        submission_id=submission.id,
        version=submission.version,
        action=action,
        comment=comment,
        acted_by_user_id=principal.user_id,
        acted_by_link_id=principal.link_id,
        acted_by_label=principal.label,
    )


async def request_revision(
    db: AsyncSession,
    principal: ClientPrincipal,
    submission_id: str,
    comment: str,
) -> ClientApprovalRecord:
    submission = await assert_shared(db, principal.project_id, submission_id)
    # R87[M10]: the only decision path missing the R69[1] gate — the guarded
    # status UPDATE below correctly no-ops on DRAFT, but the append-only
    # RECORD still landed (a decision on unreviewable content polluting the
    # approval history and the notification stream).
    _assert_decidable(submission, "request revision on")
    await _assert_no_final(db, principal.project_id)
    # R69[4]: same-version repeat is a no-op (comment traffic belongs in
    # comments; the DECISION for this version is already recorded).
    prior = (
        await db.execute(
            select(ClientApprovalRecord)
            .where(
                ClientApprovalRecord.submission_id == submission.id,
                ClientApprovalRecord.version == submission.version,
                ClientApprovalRecord.action == "revision_requested",
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if prior is not None:
        return prior
    record = _record(principal, submission, "revision_requested", comment)
    db.add(record)
    # Guarded status transition: only a SUBMITTED/APPROVED submission moves
    await db.execute(
        update(Submission)
        .where(
            Submission.id == submission.id,
            Submission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.APPROVED]),
        )
        .values(status=SubmissionStatus.REVISION_REQUESTED)
    )
    await _notify_org(db, principal, submission, "client_revision_requested")
    await db.flush()
    return record


def _assert_decidable(submission: Submission, action: str) -> None:
    """R69[1]: client decisions are only meaningful on work the creator has
    actually submitted. Approving/final-accepting a DRAFT (or an already
    revision-requested version the creator is still editing) recorded a
    decision on content the client never saw in reviewable form — and
    final-accept then completed the whole brief off a draft."""
    if submission.status not in (SubmissionStatus.SUBMITTED, SubmissionStatus.APPROVED):
        raise AppError(
            "SUBMISSION_NOT_REVIEWABLE",
            f"Cannot {action} a submission in status '{submission.status.value}'",
            409,
        )


async def approve(
    db: AsyncSession,
    principal: ClientPrincipal,
    submission_id: str,
    comment: str | None,
) -> ClientApprovalRecord:
    submission = await assert_shared(db, principal.project_id, submission_id)
    _assert_decidable(submission, "approve")
    await _assert_no_final(db, principal.project_id)
    # R69[4]: repeated identical decisions are idempotent no-ops — each call
    # previously inserted another append-only record and re-fanned up to 50
    # org notifications (unbounded spam from one client clicking approve).
    prior = (
        await db.execute(
            select(ClientApprovalRecord)
            .where(
                ClientApprovalRecord.submission_id == submission.id,
                ClientApprovalRecord.version == submission.version,
                ClientApprovalRecord.action == "approved",
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if prior is not None:
        return prior
    record = _record(principal, submission, "approved", comment)
    db.add(record)
    await _notify_org(db, principal, submission, "client_approved")
    await db.flush()
    return record


async def final_accept(
    db: AsyncSession,
    principal: ClientPrincipal,
    submission_id: str,
    comment: str | None,
) -> ClientApprovalRecord:
    """Single final acceptance per project (partial unique index — a losing
    racer gets IntegrityError mapped to 409). Completes the client brief."""
    submission = await assert_shared(db, principal.project_id, submission_id)
    _assert_decidable(submission, "final-accept")
    record = _record(principal, submission, "final_accepted", comment)
    from sqlalchemy.exc import IntegrityError

    try:
        # Nested savepoint: a losing racer's IntegrityError must not poison
        # the outer transaction (PendingRollbackError on the next statement).
        async with db.begin_nested():
            db.add(record)
            await db.flush()
    except IntegrityError as exc:
        raise AppError(
            "FINAL_ACCEPT_CONFLICT", "Project already has a final acceptance", 409
        ) from exc
    # Brief transition (REVIEW/ACTIVE/IN_PRODUCTION → COMPLETED where legal)
    project = await db.get(Project, principal.project_id)
    if project is not None and project.client_brief_id:
        from app.models.client_brief import BriefStatus, ClientBrief

        await db.execute(
            update(ClientBrief)
            .where(
                ClientBrief.id == project.client_brief_id,
                ClientBrief.status.in_(
                    [BriefStatus.REVIEW, BriefStatus.ACTIVE, BriefStatus.IN_PRODUCTION]
                ),
            )
            .values(status=BriefStatus.COMPLETED)
        )
    await _notify_org(db, principal, submission, "client_final_accepted")
    return record


async def _notify_org(
    db: AsyncSession, principal: ClientPrincipal, submission: Submission, event: str
) -> None:
    """Notify org instructors/admins of client actions (reuses product
    NotificationService — models only rule has a narrow exception here since
    NotificationService is a thin insert helper; ADR-noted)."""
    try:
        from app.models.organization import MemberStatus, OrgMember, OrgRole
        from app.services.notification import NotificationService

        recipients = (
            (
                await db.execute(
                    select(OrgMember.user_id).where(
                        OrgMember.org_id == submission.org_id,
                        OrgMember.status == MemberStatus.ACTIVE,
                        OrgMember.role.in_([OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR]),
                    )
                )
            )
            .scalars()
            .all()
        )
        svc = NotificationService(db)
        # R95[m9]: the submission CREATOR is the person who must act on a
        # revision request (their submission just flipped to
        # REVISION_REQUESTED) — they were never notified unless they happened
        # to hold a staff role. Always include them first.
        notify_ids = list(recipients[:50])
        if submission.user_id and submission.user_id not in notify_ids:
            notify_ids.insert(0, submission.user_id)
        for user_id in notify_ids:
            await svc.create(
                user_id=user_id,
                notification_type=event,
                title=f"Client action: {event.replace('_', ' ')}",
                body=f"{principal.label} acted on submission v{submission.version}",
                org_id=submission.org_id,
                data={"project_id": submission.project_id, "submission_id": submission.id},
            )
    except Exception:  # noqa: BLE001 — notifications must never fail the decision
        log.warning("cp_portal_notify_failed", event=event, exc_info=True)
