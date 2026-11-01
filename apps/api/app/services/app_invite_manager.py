"""App Invite Manager — manage user invitations for installed apps.

Handles invite lifecycle:
- Create invites with roles and expiry
- Accept/decline/revoke invites
- Per-installation scoped invites
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class InviteStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class Invite:
    """A user invitation."""

    invite_id: str
    installation_id: str
    email: str
    role: str
    token: str
    status: InviteStatus = InviteStatus.PENDING
    invited_by: str = ""
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    responded_at: float | None = None


class AppInviteManager:
    """Manage user invitations for installed apps."""

    def __init__(self, expiry_hours: int = 72) -> None:
        self._expiry_seconds = expiry_hours * 3600
        self._invites: dict[tuple[str, str], Invite] = {}
        self._token_index: dict[str, tuple[str, str]] = {}

    def create_invite(
        self,
        installation_id: str,
        invite_id: str,
        email: str,
        role: str = "member",
        invited_by: str = "",
        now: float | None = None,
    ) -> Invite:
        ALLOWED_ROLES = {"viewer", "member", "admin"}
        if not installation_id:
            raise ValueError("installation_id is required")
        if not invite_id:
            raise ValueError("invite_id is required")
        if not email:
            raise ValueError("email is required")
        if role not in ALLOWED_ROLES:
            raise ValueError(f"Invalid role: {role}. Must be one of {ALLOWED_ROLES}")

        key = (installation_id, invite_id)
        if key in self._invites:
            raise ValueError(f"Invite {invite_id} already exists")

        now = now or time.time()
        token = secrets.token_urlsafe(32)
        invite = Invite(
            invite_id=invite_id, installation_id=installation_id,
            email=email, role=role, token=token, invited_by=invited_by,
            created_at=now, expires_at=now + self._expiry_seconds,
        )
        self._invites[key] = invite
        self._token_index[token] = key
        return invite

    def accept_invite(self, token: str, accepting_email: str, now: float | None = None) -> Invite:
        invite = self._get_by_token(token, now)
        if accepting_email.strip().lower() != invite.email.strip().lower():
            raise PermissionError("Invite not addressed to this user")
        if invite.status != InviteStatus.PENDING:
            raise ValueError(f"Cannot accept invite in {invite.status} state")
        invite.status = InviteStatus.ACCEPTED
        invite.responded_at = now or time.time()
        return invite

    def decline_invite(self, token: str, declining_email: str, now: float | None = None) -> Invite:
        invite = self._get_by_token(token, now)
        if declining_email.strip().lower() != invite.email.strip().lower():
            raise PermissionError("Invite not addressed to this user")
        if invite.status != InviteStatus.PENDING:
            raise ValueError(f"Cannot decline invite in {invite.status} state")
        invite.status = InviteStatus.DECLINED
        invite.responded_at = now or time.time()
        return invite

    def revoke_invite(self, installation_id: str, invite_id: str) -> Invite:
        invite = self._get(installation_id, invite_id)
        if invite.status != InviteStatus.PENDING:
            raise ValueError(f"Cannot revoke invite in {invite.status} state")
        invite.status = InviteStatus.REVOKED
        return invite

    def list_invites(self, installation_id: str, status: InviteStatus | None = None) -> list[Invite]:
        invites = [i for (inst, _), i in self._invites.items() if inst == installation_id]
        if status:
            invites = [i for i in invites if i.status == status]
        return invites

    def _get(self, installation_id: str, invite_id: str) -> Invite:
        key = (installation_id, invite_id)
        invite = self._invites.get(key)
        if invite is None:
            raise KeyError(f"Invite {invite_id} not found")
        return invite

    def _get_by_token(self, token: str, now: float | None = None) -> Invite:
        key = self._token_index.get(token)
        if key is None:
            raise KeyError("Invalid invite token")
        invite = self._invites[key]
        now = now or time.time()
        if now >= invite.expires_at and invite.status == InviteStatus.PENDING:
            invite.status = InviteStatus.EXPIRED
        return invite
