"""Organization service — CRUD, membership, invitations."""

import re
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.email import get_email_sender
from app.exceptions import AppError
from app.models.organization import (
    ROLE_HIERARCHY,
    InviteStatus,
    MemberStatus,
    Organization,
    OrgInvitation,
    OrgInviteLink,
    OrgMember,
    OrgRole,
    OrgStatus,
)
from app.models.user import User

log = structlog.get_logger()


# ── Errors ────────────────────────────────────────────────────


class OrgNotFoundError(AppError):
    def __init__(self):
        super().__init__("ORG_NOT_FOUND", "Organization not found", 404)


class SlugAlreadyExistsError(AppError):
    def __init__(self):
        super().__init__("SLUG_ALREADY_EXISTS", "An organization with this slug already exists", 409)


class AlreadyMemberError(AppError):
    def __init__(self):
        super().__init__("ALREADY_MEMBER", "User is already a member of this organization", 409)


class CannotRemoveOwnerError(AppError):
    def __init__(self):
        super().__init__("CANNOT_REMOVE_OWNER", "Cannot remove the organization owner", 422)


class InsufficientOrgPermissionError(AppError):
    def __init__(self):
        super().__init__("INSUFFICIENT_ORG_PERMISSION", "Insufficient organization permissions", 403)


class InviteLinkInvalidError(AppError):
    def __init__(self, detail: str = "Invalid or expired invite link"):
        super().__init__("INVITE_LINK_INVALID", detail, 422)


class InviteTokenInvalidError(AppError):
    def __init__(self, detail: str = "Invalid or expired invite token"):
        super().__init__("INVITE_TOKEN_INVALID", detail, 422)


# ── DTOs ──────────────────────────────────────────────────────


@dataclass
class InviteResult:
    invited: int
    already_member: int
    already_invited: int


# ── Service ───────────────────────────────────────────────────


class OrgService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── CRUD ──

    async def create(
        self, name: str, slug: str | None, description: str | None, created_by: str
    ) -> Organization:
        if slug is None:
            slug = self._generate_slug(name)

        # Check slug uniqueness
        existing = await self.db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        if existing.scalar_one_or_none() is not None:
            raise SlugAlreadyExistsError()

        org = Organization(
            name=name,
            slug=slug,
            description=description,
            created_by=created_by,
        )
        self.db.add(org)
        await self.db.flush()

        # Creator becomes owner
        member = OrgMember(
            org_id=org.id,
            user_id=created_by,
            role=OrgRole.OWNER,
            status=MemberStatus.ACTIVE,
        )
        self.db.add(member)
        await self.db.flush()

        log.info("org_created", org_id=org.id, slug=org.slug, by=created_by)
        return org

    async def get_user_orgs(self, user_id: str) -> list[dict]:
        """Get all orgs the user belongs to, with their role and member count."""
        stmt = (
            select(
                Organization,
                OrgMember.role,
                func.count(OrgMember.id).over(partition_by=Organization.id).label("member_count"),
            )
            .join(OrgMember, OrgMember.org_id == Organization.id)
            .where(OrgMember.user_id == user_id, OrgMember.status == MemberStatus.ACTIVE)
            .order_by(Organization.created_at.desc())
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        seen = set()
        orgs = []
        for org, role, count in rows:
            if org.id not in seen:
                seen.add(org.id)
                orgs.append({"org": org, "role": role.value, "member_count": count})
        return orgs

    async def get_org(self, org_id: str) -> Organization:
        org = await self.db.get(Organization, org_id)
        if org is None:
            raise OrgNotFoundError()
        return org

    async def update_org(self, org_id: str, **fields) -> Organization:
        org = await self.get_org(org_id)
        for key, value in fields.items():
            if value is not None and hasattr(org, key):
                setattr(org, key, value)
        await self.db.flush()
        return org

    async def delete_org(self, org_id: str, user_id: str) -> None:
        org = await self.get_org(org_id)
        member = await self._get_active_member(org_id, user_id)
        if member.role != OrgRole.OWNER:
            raise InsufficientOrgPermissionError()

        org.status = OrgStatus.ARCHIVED
        await self.db.flush()
        log.info("org_deleted", org_id=org_id, by=user_id)

    # ── Members ──

    async def add_member(
        self, org_id: str, user_id: str, role: OrgRole, invited_by: str | None = None
    ) -> OrgMember:
        # Check existing
        stmt = select(OrgMember).where(
            OrgMember.org_id == org_id, OrgMember.user_id == user_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            if existing.status == MemberStatus.ARCHIVED:
                existing.status = MemberStatus.ACTIVE
                existing.role = role
                await self.db.flush()
                return existing
            raise AlreadyMemberError()

        member = OrgMember(
            org_id=org_id,
            user_id=user_id,
            role=role,
            status=MemberStatus.ACTIVE,
            invited_by=invited_by,
        )
        self.db.add(member)
        await self.db.flush()
        return member

    async def remove_member(self, org_id: str, user_id: str, removed_by: str) -> None:
        member = await self._get_active_member(org_id, user_id)

        if member.role == OrgRole.OWNER:
            raise CannotRemoveOwnerError()

        if user_id != removed_by:
            actor = await self._get_active_member(org_id, removed_by)
            if not self._can_manage_member(actor, member):
                raise InsufficientOrgPermissionError()

        member.status = MemberStatus.ARCHIVED
        await self.db.flush()
        log.info("org_member_removed", org_id=org_id, user_id=user_id, by=removed_by)

    async def update_member_role(
        self, org_id: str, user_id: str, new_role: OrgRole, changed_by: str
    ) -> OrgMember:
        actor = await self._get_active_member(org_id, changed_by)
        if actor.role != OrgRole.OWNER:
            raise InsufficientOrgPermissionError()

        member = await self._get_active_member(org_id, user_id)
        old_role = member.role
        member.role = new_role
        await self.db.flush()

        log.info(
            "org_member_role_changed",
            org_id=org_id,
            user_id=user_id,
            old=old_role.value,
            new=new_role.value,
            by=changed_by,
        )
        return member

    async def get_members(
        self, org_id: str, page: int = 1, per_page: int = 20, role: str | None = None
    ) -> tuple[list, int]:
        offset = (page - 1) * per_page
        base = select(OrgMember).where(
            OrgMember.org_id == org_id, OrgMember.status == MemberStatus.ACTIVE
        )
        if role:
            base = base.where(OrgMember.role == OrgRole(role))

        total_result = await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()

        result = await self.db.execute(
            base.order_by(OrgMember.joined_at.desc()).offset(offset).limit(per_page)
        )
        members = result.scalars().all()
        return list(members), total

    async def get_member_count(self, org_id: str) -> int:
        result = await self.db.execute(
            select(func.count(OrgMember.id)).where(
                OrgMember.org_id == org_id, OrgMember.status == MemberStatus.ACTIVE
            )
        )
        return result.scalar_one()

    # ── Invitations ──

    async def invite_members(
        self, org_id: str, emails: list[str], role: OrgRole, invited_by: str
    ) -> InviteResult:
        invited = 0
        already_member = 0
        already_invited = 0
        sender = get_email_sender()

        for email in emails:
            # Check if already a member
            user_result = await self.db.execute(select(User).where(User.email == email))
            user = user_result.scalar_one_or_none()

            if user:
                member_result = await self.db.execute(
                    select(OrgMember).where(
                        OrgMember.org_id == org_id,
                        OrgMember.user_id == user.id,
                        OrgMember.status == MemberStatus.ACTIVE,
                    )
                )
                if member_result.scalar_one_or_none():
                    already_member += 1
                    continue

            # Check if already invited
            existing_invite = await self.db.execute(
                select(OrgInvitation).where(
                    OrgInvitation.org_id == org_id,
                    OrgInvitation.email == email,
                    OrgInvitation.status == InviteStatus.PENDING,
                )
            )
            if existing_invite.scalar_one_or_none():
                already_invited += 1
                continue

            # Create invitation
            raw_token = secrets.token_urlsafe(32)
            invitation = OrgInvitation(
                org_id=org_id,
                email=email,
                role=role,
                token_hash=sha256(raw_token.encode()).hexdigest(),
                invited_by=invited_by,
                expires_at=datetime.now(UTC) + timedelta(days=7),
            )
            self.db.add(invitation)

            # Send email (escape user-controlled values to prevent HTML injection)
            from html import escape

            from app.config import settings as app_settings

            org = await self.get_org(org_id)
            invite_url = f"{app_settings.frontend_url}/api/v1/invites/accept?token={raw_token}"
            safe_name = escape(org.name)
            await sender.send(
                to=email,
                subject=f"You're invited to join {org.name} on OpenSkill Studio",
                html=f"<p>You've been invited to join <strong>{safe_name}</strong>. "
                f'Click <a href="{escape(invite_url)}">here</a> to accept.</p>',
            )
            invited += 1

        await self.db.flush()
        return InviteResult(invited=invited, already_member=already_member, already_invited=already_invited)

    async def get_invitations(self, org_id: str) -> list[OrgInvitation]:
        result = await self.db.execute(
            select(OrgInvitation)
            .where(OrgInvitation.org_id == org_id, OrgInvitation.status == InviteStatus.PENDING)
            .order_by(OrgInvitation.created_at.desc())
        )
        return list(result.scalars().all())

    async def revoke_invitation(self, org_id: str, invite_id: str) -> None:
        invite = await self.db.get(OrgInvitation, invite_id)
        if invite is None or invite.org_id != org_id:
            raise AppError("INVITE_NOT_FOUND", "Invitation not found", 404)
        invite.status = InviteStatus.REVOKED
        await self.db.flush()

    async def accept_email_invite(self, raw_token: str, user_id: str) -> OrgMember:
        token_hash = sha256(raw_token.encode()).hexdigest()
        result = await self.db.execute(
            select(OrgInvitation).where(OrgInvitation.token_hash == token_hash)
        )
        invite = result.scalar_one_or_none()

        if invite is None:
            raise InviteTokenInvalidError("Invitation not found")
        if invite.status != InviteStatus.PENDING:
            raise InviteTokenInvalidError("Invitation already used or revoked")
        if invite.expires_at < datetime.now(UTC):
            invite.status = InviteStatus.EXPIRED
            await self.db.flush()
            raise InviteTokenInvalidError("Invitation has expired")

        # Verify the accepting user matches the invited email
        user = await self.db.get(User, user_id)
        if user is None or user.email.lower() != invite.email.lower():
            raise InviteTokenInvalidError("Invitation is not addressed to this account")

        invite.status = InviteStatus.ACCEPTED
        invite.accepted_at = datetime.now(UTC)

        member = await self.add_member(
            org_id=invite.org_id,
            user_id=user_id,
            role=invite.role,
            invited_by=invite.invited_by,
        )
        await self.db.flush()
        return member

    # ── Invite Links ──

    async def create_invite_link(
        self,
        org_id: str,
        role: OrgRole,
        max_uses: int | None,
        expires_in_days: int | None,
        created_by: str,
    ) -> OrgInviteLink:
        code = secrets.token_urlsafe(12)[:16]
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(UTC) + timedelta(days=expires_in_days)

        link = OrgInviteLink(
            org_id=org_id,
            code=code,
            role=role,
            max_uses=max_uses,
            expires_at=expires_at,
            created_by=created_by,
        )
        self.db.add(link)
        await self.db.flush()
        return link

    async def get_invite_links(self, org_id: str) -> list[OrgInviteLink]:
        result = await self.db.execute(
            select(OrgInviteLink)
            .where(OrgInviteLink.org_id == org_id)
            .order_by(OrgInviteLink.created_at.desc())
        )
        return list(result.scalars().all())

    async def toggle_invite_link(self, org_id: str, link_id: str, is_active: bool) -> OrgInviteLink:
        link = await self.db.get(OrgInviteLink, link_id)
        if link is None or link.org_id != org_id:
            raise AppError("LINK_NOT_FOUND", "Invite link not found", 404)
        link.is_active = is_active
        await self.db.flush()
        return link

    async def delete_invite_link(self, org_id: str, link_id: str) -> None:
        link = await self.db.get(OrgInviteLink, link_id)
        if link is None or link.org_id != org_id:
            raise AppError("LINK_NOT_FOUND", "Invite link not found", 404)
        await self.db.delete(link)
        await self.db.flush()

    async def join_by_code(self, code: str, user_id: str) -> OrgMember:
        result = await self.db.execute(
            select(OrgInviteLink).where(OrgInviteLink.code == code)
        )
        link = result.scalar_one_or_none()

        if link is None or not link.is_active:
            raise InviteLinkInvalidError("Invite link not found or inactive")
        if link.expires_at and link.expires_at < datetime.now(UTC):
            raise InviteLinkInvalidError("Invite link has expired")
        if link.max_uses and link.use_count >= link.max_uses:
            raise InviteLinkInvalidError("Invite link has reached maximum uses")

        member = await self.add_member(
            org_id=link.org_id, user_id=user_id, role=link.role
        )
        link.use_count += 1
        await self.db.flush()
        return member

    # ── Settings ──

    async def update_settings(self, org_id: str, settings: dict) -> Organization:
        org = await self.get_org(org_id)
        current = org.settings or {}
        current.update(settings)
        org.settings = current
        await self.db.flush()
        return org

    # ── Helpers ──

    async def _get_active_member(self, org_id: str, user_id: str) -> OrgMember:
        result = await self.db.execute(
            select(OrgMember).where(
                OrgMember.org_id == org_id,
                OrgMember.user_id == user_id,
                OrgMember.status == MemberStatus.ACTIVE,
            )
        )
        member = result.scalar_one_or_none()
        if member is None:
            raise InsufficientOrgPermissionError()
        return member

    def _can_manage_member(self, actor: OrgMember, target: OrgMember) -> bool:
        """Can only manage members strictly below your role in the hierarchy."""
        return ROLE_HIERARCHY.get(actor.role, 99) < ROLE_HIERARCHY.get(target.role, 99)

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:100]
