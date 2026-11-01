"""App API Developer Invite — invite developers to the platform."""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeveloperInvite:
    invite_id: str
    email: str
    role: str = "developer"
    code: str = field(default_factory=lambda: secrets.token_urlsafe(16))
    accepted: bool = False
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperInvite:
    def __init__(self) -> None:
        self._invites: dict[tuple[str, str], DeveloperInvite] = {}

    def create(self, installation_id: str, invite_id: str, email: str, role: str = "developer") -> DeveloperInvite:
        if not installation_id: raise ValueError("installation_id is required")
        if not email or "@" not in email: raise ValueError("valid email required")
        key = (installation_id, invite_id)
        if key in self._invites: raise ValueError(f"Invite {invite_id} already exists")
        inv = DeveloperInvite(invite_id=invite_id, email=email, role=role)
        self._invites[key] = inv
        return inv

    def accept(self, installation_id: str, code: str) -> DeveloperInvite:
        for (inst, _), inv in self._invites.items():
            if inst == installation_id and inv.code == code and not inv.accepted:
                inv.accepted = True
                return inv
        raise KeyError("Invalid or already used invite code")

    def pending(self, installation_id: str) -> list[DeveloperInvite]:
        return [i for (inst, _), i in self._invites.items() if inst == installation_id and not i.accepted]

    def list_invites(self, installation_id: str) -> list[DeveloperInvite]:
        return [i for (inst, _), i in self._invites.items() if inst == installation_id]
