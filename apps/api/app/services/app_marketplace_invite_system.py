"""Invite System — manage developer invitations and beta access for extensions.

Supports invite codes, beta programs, waitlists, and capacity-controlled
access for extensions before public release.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import secrets


@dataclass
class InviteCode:
    code: str
    extension_id: str
    created_by: str
    max_uses: int
    used_count: int = 0
    created_at: str = ""
    expires_at: str = ""
    active: bool = True

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class BetaProgram:
    extension_id: str
    name: str
    capacity: int
    enrolled: list[str] = field(default_factory=list)
    waitlist: list[str] = field(default_factory=list)
    open_enrollment: bool = False


class InviteSystem:
    """Manages invitations and beta access for extensions."""

    def __init__(self):
        self._codes: dict[str, InviteCode] = {}
        self._betas: dict[str, BetaProgram] = {}
        self._redeemed: dict[str, list[str]] = {}  # user -> [codes]

    def create_invite_code(self, extension_id: str, created_by: str,
                           max_uses: int = 10) -> InviteCode:
        code = secrets.token_urlsafe(8).upper()[:8]
        invite = InviteCode(code=code, extension_id=extension_id,
                            created_by=created_by, max_uses=max_uses)
        self._codes[code] = invite
        return invite

    def redeem_code(self, code: str, user_id: str) -> tuple[bool, str]:
        invite = self._codes.get(code)
        if not invite or not invite.active:
            return False, "Invalid or inactive invite code"
        if invite.used_count >= invite.max_uses:
            return False, "Invite code has reached maximum uses"
        # Check if user already redeemed this code
        user_codes = self._redeemed.get(user_id, [])
        if code in user_codes:
            return False, "You have already redeemed this code"
        invite.used_count += 1
        self._redeemed.setdefault(user_id, []).append(code)
        return True, f"Access granted to {invite.extension_id}"

    def deactivate_code(self, code: str) -> bool:
        invite = self._codes.get(code)
        if invite:
            invite.active = False
            return True
        return False

    def create_beta(self, extension_id: str, name: str, capacity: int,
                    open_enrollment: bool = False) -> BetaProgram:
        beta = BetaProgram(extension_id=extension_id, name=name,
                           capacity=capacity, open_enrollment=open_enrollment)
        self._betas[extension_id] = beta
        return beta

    def enroll_beta(self, extension_id: str, user_id: str) -> tuple[bool, str]:
        beta = self._betas.get(extension_id)
        if not beta:
            return False, "Beta program not found"
        if user_id in beta.enrolled:
            return False, "Already enrolled"
        if len(beta.enrolled) >= beta.capacity:
            if user_id not in beta.waitlist:
                beta.waitlist.append(user_id)
            return False, "Beta is full, added to waitlist"
        beta.enrolled.append(user_id)
        return True, "Enrolled in beta"

    def get_beta_status(self, extension_id: str) -> dict | None:
        beta = self._betas.get(extension_id)
        if not beta:
            return None
        return {
            "extension_id": extension_id, "name": beta.name,
            "capacity": beta.capacity, "enrolled": len(beta.enrolled),
            "waitlisted": len(beta.waitlist),
            "available_slots": max(0, beta.capacity - len(beta.enrolled)),
        }
