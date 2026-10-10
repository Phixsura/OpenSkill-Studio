"""Identity resolution (ADR-018 §9).

resolve() turns a verified external identity into a platform user —
link-first (stable subject), verified-email match second, JIT third,
admin queue for everything ambiguous. Takeover invariants (tested):
- an UNVERIFIED IdP email never links or matches;
- email matching only applies when the email's domain is VERIFIED for the org;
- an email/UPN change at the IdP never re-links (subject is the key);
- the same subject in two orgs is two independent links;
- JIT can mint at most JIT_ALLOWED_ROLES (never owner/admin).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models import (
    JIT_ALLOWED_ROLES,
    ExternalIdentityLink,
    IdentityMatchQueue,
)
from app.integrations.services.domains import OrgDomainService
from app.models.organization import MemberStatus, OrgMember, OrgRole
from app.models.user import User, UserRole, UserStatus

log = structlog.get_logger()


@dataclass
class VerifiedExternalIdentity:
    """Normalized output of any SSO/provisioning protocol handler."""

    org_id: str
    source: str  # sso | scim | roster | lti | ats
    connection_ref: str
    subject: str
    email: str | None
    email_verified: bool
    display_name: str | None = None
    external_id: str | None = None
    attrs: dict = field(default_factory=dict)


@dataclass
class ResolutionResult:
    user: User
    link: ExternalIdentityLink
    jit_created: bool


class IdentityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve(
        self,
        ident: VerifiedExternalIdentity,
        *,
        allow_jit: bool = False,
        jit_role: str = "student",
    ) -> ResolutionResult:
        # Defensive claim coercion (review defect #3): IdP/LMS claims are
        # untrusted JSON — a non-string email/display_name must degrade to
        # None (queueing), never reach a DB column as a dict/list (500).
        if not isinstance(ident.email, str) or len(ident.email) > 255:
            ident.email = None
            ident.email_verified = False
        if not isinstance(ident.display_name, str):
            ident.display_name = None
        else:
            ident.display_name = ident.display_name[:100] or None
        if not isinstance(ident.subject, str) or not ident.subject or len(ident.subject) > 500:
            raise AppError("IDENTITY_AMBIGUOUS", "Invalid external subject", 403)

        # 1. Hot path: active link for (connection, subject).
        link = (
            await self.db.execute(
                select(ExternalIdentityLink).where(
                    ExternalIdentityLink.connection_ref == ident.connection_ref,
                    ExternalIdentityLink.subject == ident.subject,
                    ExternalIdentityLink.revoked_at.is_(None),
                )
            )
        ).scalar_one_or_none()
        if link is not None:
            user = await self.db.get(User, link.user_id)
            if user is None or user.status != UserStatus.ACTIVE:
                raise AppError("SSO_NO_ACCOUNT", "Linked account is unavailable", 403)
            return ResolutionResult(user=user, link=link, jit_created=False)

        # 2. Verified-email match — ONLY a verified IdP email whose domain is
        # verified for this org participates (takeover guard).
        email = (ident.email or "").strip().lower()
        domain = email.rsplit("@", 1)[-1] if "@" in email else ""
        verified_domains = await OrgDomainService(self.db).verified_domains(ident.org_id)
        if not ident.email_verified or not email or domain not in verified_domains:
            await self._queue(ident, reason="email_unverified_or_foreign_domain")
            raise AppError("IDENTITY_AMBIGUOUS", "Identity requires admin confirmation", 403)

        members = (
            await self.db.execute(
                select(User)
                .join(OrgMember, OrgMember.user_id == User.id)
                .where(
                    OrgMember.org_id == ident.org_id,
                    OrgMember.status == MemberStatus.ACTIVE,
                    func.lower(User.email) == email,
                    User.status == UserStatus.ACTIVE,
                )
            )
        ).scalars().all()

        if len(members) == 1:
            return ResolutionResult(
                user=members[0],
                link=await self._link(ident, members[0].id),
                jit_created=False,
            )
        if len(members) > 1:
            await self._queue(ident, reason="multiple_member_matches")
            raise AppError("IDENTITY_AMBIGUOUS", "Identity requires admin confirmation", 403)

        # 3. Zero matches: JIT or refuse.
        if not allow_jit:
            await self._queue(ident, reason="no_member_match")
            raise AppError("SSO_NO_ACCOUNT", "No account for this identity", 403)
        user = await self._jit_provision(ident, jit_role)
        return ResolutionResult(
            user=user, link=await self._link(ident, user.id), jit_created=True
        )

    async def _link(self, ident: VerifiedExternalIdentity, user_id: str) -> ExternalIdentityLink:
        link = ExternalIdentityLink(
            org_id=ident.org_id,
            user_id=user_id,
            source=ident.source,
            connection_ref=ident.connection_ref,
            subject=ident.subject,
            external_id=ident.external_id,
            email_at_link=ident.email,
        )
        self.db.add(link)
        try:
            async with self.db.begin_nested():
                await self.db.flush()
        except Exception:
            # Concurrent first-login race: the partial unique index arbitrates;
            # the loser re-reads the winner's link (upsert-not-select-then-insert).
            existing = (
                await self.db.execute(
                    select(ExternalIdentityLink).where(
                        ExternalIdentityLink.connection_ref == ident.connection_ref,
                        ExternalIdentityLink.subject == ident.subject,
                        ExternalIdentityLink.revoked_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if existing is None:
                raise
            return existing
        return link

    async def _jit_provision(self, ident: VerifiedExternalIdentity, jit_role: str) -> User:
        if jit_role not in JIT_ALLOWED_ROLES:
            # Role-mint ceiling (R88 class 4): config drift can never escalate.
            raise AppError("SSO_JIT_ROLE_INVALID", "JIT role not allowed", 422)
        email = (ident.email or "").strip().lower()
        existing = (
            await self.db.execute(select(User).where(func.lower(User.email) == email))
        ).scalar_one_or_none()
        if existing is not None:
            # A platform account exists but is NOT a member of this org.
            # Membership-only JIT: add membership, never touch credentials.
            if existing.status != UserStatus.ACTIVE:
                await self._queue(ident, reason="existing_account_inactive")
                raise AppError("IDENTITY_AMBIGUOUS", "Identity requires admin confirmation", 403)
            user = existing
        else:
            user = User(
                email=email,
                password_hash=None,
                display_name=ident.display_name or email.split("@", 1)[0],
                role=UserRole.STUDENT,
                status=UserStatus.ACTIVE,
                email_verified=True,  # verified domain + verified IdP email
            )
            self.db.add(user)
            await self.db.flush()
        member = (
            await self.db.execute(
                select(OrgMember).where(
                    OrgMember.org_id == ident.org_id, OrgMember.user_id == user.id
                )
            )
        ).scalar_one_or_none()
        if member is None:
            self.db.add(
                OrgMember(
                    org_id=ident.org_id,
                    user_id=user.id,
                    role=OrgRole(jit_role),
                    status=MemberStatus.ACTIVE,
                )
            )
            await self.db.flush()
        return user

    async def _queue(self, ident: VerifiedExternalIdentity, *, reason: str) -> None:
        dup = (
            await self.db.execute(
                select(IdentityMatchQueue.id).where(
                    IdentityMatchQueue.connection_ref == ident.connection_ref,
                    IdentityMatchQueue.subject == ident.subject,
                    IdentityMatchQueue.status == "pending",
                )
            )
        ).scalar_one_or_none()
        if dup is not None:
            return  # one pending row per subject — retried logins don't spam
        self.db.add(
            IdentityMatchQueue(
                org_id=ident.org_id,
                source=ident.source,
                connection_ref=ident.connection_ref,
                subject=ident.subject,
                email=ident.email,
                reason=reason,
                payload={"display_name": ident.display_name, "external_id": ident.external_id},
            )
        )
        await self.db.flush()

    # ── link administration (ADR §2.5: linking is REVERSIBLE) ──

    async def list_links(
        self, org_id: str, *, user_id: str | None = None
    ) -> list[ExternalIdentityLink]:
        q = (
            select(ExternalIdentityLink)
            .where(
                ExternalIdentityLink.org_id == org_id,
                ExternalIdentityLink.revoked_at.is_(None),
            )
            .order_by(ExternalIdentityLink.created_at.desc())
            .limit(500)
        )
        if user_id:
            q = q.where(ExternalIdentityLink.user_id == user_id)
        return list((await self.db.execute(q)).scalars())

    async def unlink(self, org_id: str, link_id: str) -> ExternalIdentityLink:
        """Revoke (not delete): history survives for audit; the partial
        unique index frees (connection, subject) for a future re-link."""
        link = await self.db.get(ExternalIdentityLink, link_id)
        if link is None or link.org_id != org_id or link.revoked_at is not None:
            raise AppError("IDENTITY_LINK_NOT_FOUND", "Link not found", 404)
        link.revoked_at = datetime.now(UTC)
        await self.db.flush()
        return link

    # ── admin queue resolution ──

    async def list_queue(self, org_id: str, status: str = "pending") -> list[IdentityMatchQueue]:
        return list(
            (
                await self.db.execute(
                    select(IdentityMatchQueue)
                    .where(
                        IdentityMatchQueue.org_id == org_id,
                        IdentityMatchQueue.status == status,
                    )
                    .order_by(IdentityMatchQueue.created_at)
                )
            ).scalars()
        )

    async def resolve_queue_item(
        self, org_id: str, item_id: str, *, action: str, user_id: str | None, actor_id: str
    ) -> IdentityMatchQueue:
        item = await self.db.get(IdentityMatchQueue, item_id)
        if item is None or item.org_id != org_id:
            raise AppError("IDENTITY_QUEUE_NOT_FOUND", "Queue item not found", 404)
        if item.status != "pending":
            raise AppError("IDENTITY_QUEUE_RESOLVED", "Queue item already resolved", 409)
        if action == "link":
            if not user_id:
                raise AppError("IDENTITY_QUEUE_INVALID", "user_id required for link", 422)
            member = (
                await self.db.execute(
                    select(OrgMember).where(
                        OrgMember.org_id == org_id,
                        OrgMember.user_id == user_id,
                        OrgMember.status == MemberStatus.ACTIVE,
                    )
                )
            ).scalar_one_or_none()
            if member is None:
                raise AppError("IDENTITY_QUEUE_INVALID", "Target is not an active member", 422)
            ident = VerifiedExternalIdentity(
                org_id=org_id,
                source=item.source,
                connection_ref=item.connection_ref,
                subject=item.subject,
                email=item.email,
                email_verified=False,
            )
            await self._link(ident, user_id)
            item.status = "linked"
        elif action == "reject":
            item.status = "rejected"
        else:
            raise AppError("IDENTITY_QUEUE_INVALID", "action must be link|reject", 422)
        item.resolved_by = actor_id
        item.resolved_at = datetime.now(UTC)
        await self.db.flush()
        return item
