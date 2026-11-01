"""App Invite Link — manage shareable invitation links.

Manages invite links:
- Generate unique invite links with expiration
- Track usage (claims)
- Limit max uses per link
- Per-installation scoped links
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class InviteLink:
    """A shareable invitation link."""

    invite_id: str
    code: str
    role: str = "member"
    max_uses: int = 0  # 0 = unlimited
    uses: int = 0
    expires_at: float | None = None
    created_by: str = ""
    created_at: float = field(default_factory=time.time)
    revoked: bool = False

    @property
    def is_valid(self) -> bool:
        if self.revoked:
            return False
        if self.expires_at and time.time() > self.expires_at:
            return False
        if self.max_uses > 0 and self.uses >= self.max_uses:
            return False
        return True


class AppInviteLink:
    """Manage shareable invitation links."""

    def __init__(self) -> None:
        self._links: dict[tuple[str, str], InviteLink] = {}

    def create(
        self, installation_id: str, invite_id: str, role: str = "member",
        max_uses: int = 0, ttl_seconds: int | None = None, created_by: str = "",
    ) -> InviteLink:
        if not installation_id:
            raise ValueError("installation_id is required")

        code = secrets.token_urlsafe(16)
        expires_at = None
        if ttl_seconds is not None:
            if ttl_seconds <= 0:
                raise ValueError("ttl_seconds must be positive")
            expires_at = time.time() + ttl_seconds

        link = InviteLink(
            invite_id=invite_id, code=code, role=role,
            max_uses=max_uses, expires_at=expires_at, created_by=created_by,
        )
        self._links[(installation_id, invite_id)] = link
        return link

    def claim(self, installation_id: str, code: str) -> InviteLink:
        """Claim an invite by code."""
        for (inst, _), link in self._links.items():
            if inst == installation_id and link.code == code:
                if not link.is_valid:
                    raise ValueError("Invite link is no longer valid")
                link.uses += 1
                return link
        raise KeyError("Invalid invite code")

    def revoke(self, installation_id: str, invite_id: str) -> InviteLink:
        key = (installation_id, invite_id)
        link = self._links.get(key)
        if link is None:
            raise KeyError(f"Invite {invite_id} not found")
        link.revoked = True
        return link

    def list_links(self, installation_id: str, valid_only: bool = False) -> list[InviteLink]:
        links = [l for (inst, _), l in self._links.items() if inst == installation_id]
        if valid_only:
            links = [l for l in links if l.is_valid]
        return links
