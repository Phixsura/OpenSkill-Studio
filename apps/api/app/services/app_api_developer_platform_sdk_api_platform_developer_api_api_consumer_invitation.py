"""API Consumer Invitation — invite new consumers to use the API."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import secrets
import time
import structlog

log = structlog.get_logger()

class InviteStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class Invitation:
    invite_id: str
    email: str
    role: str = "consumer"  # "consumer", "admin"
    status: InviteStatus = InviteStatus.PENDING
    token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    accepted_at: float = 0.0

VALID_ROLES = {"consumer", "admin", "viewer"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerInvitation:
    def __init__(self, invite_ttl_hours: int = 72) -> None:
        self._invites: dict[tuple[str, str], Invitation] = {}
        self._ttl = max(1, invite_ttl_hours) * 3600

    def create_invite(self, installation_id: str, invite_id: str, email: str, role: str = "consumer") -> Invitation:
        if not installation_id: raise ValueError("installation_id is required")
        if not email or "@" not in email: raise ValueError("Valid email required")
        if role not in VALID_ROLES: raise ValueError(f"Invalid role: {role}")
        # Check for existing pending invite
        for (inst, _), inv in self._invites.items():
            if inst == installation_id and inv.email == email and inv.status == InviteStatus.PENDING:
                raise ValueError(f"Pending invite already exists for {email}")
        now = time.time()
        inv = Invitation(invite_id=invite_id, email=email, role=role, expires_at=now + self._ttl)
        self._invites[(installation_id, invite_id)] = inv
        return inv

    def accept(self, installation_id: str, invite_id: str, token: str) -> Invitation:
        inv = self._get(installation_id, invite_id)
        if inv.status != InviteStatus.PENDING: raise ValueError(f"Invite is {inv.status.value}")
        if time.time() > inv.expires_at:
            inv.status = InviteStatus.EXPIRED
            raise ValueError("Invite has expired")
        if not secrets.compare_digest(inv.token, token): raise ValueError("Invalid token")
        inv.status = InviteStatus.ACCEPTED
        inv.accepted_at = time.time()
        return inv

    def revoke(self, installation_id: str, invite_id: str) -> Invitation:
        inv = self._get(installation_id, invite_id)
        if inv.status != InviteStatus.PENDING: raise ValueError(f"Cannot revoke {inv.status.value} invite")
        inv.status = InviteStatus.REVOKED
        return inv

    def pending_invites(self, installation_id: str) -> list[Invitation]:
        return [i for (inst, _), i in self._invites.items() if inst == installation_id and i.status == InviteStatus.PENDING]

    def _get(self, installation_id: str, invite_id: str) -> Invitation:
        inv = self._invites.get((installation_id, invite_id))
        if inv is None: raise KeyError(f"Invite {invite_id} not found")
        return inv
