"""App API Token Expiry — track and alert on expiring API tokens.

Manages token expiry:
- Register tokens with expiry dates
- Find tokens expiring soon
- Track expired tokens
- Per-installation scoped tokens
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class TokenExpiry:
    """A token with expiry tracking."""

    token_id: str
    label: str
    expires_at: float
    notified: bool = False

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    @property
    def days_remaining(self) -> int:
        remaining = (self.expires_at - time.time()) / 86400
        return max(0, int(remaining))


class AppAPITokenExpiry:
    """Track and alert on expiring API tokens."""

    def __init__(self) -> None:
        self._tokens: dict[tuple[str, str], TokenExpiry] = {}

    def register(self, installation_id: str, token_id: str, label: str, expires_at: float) -> TokenExpiry:
        if not installation_id:
            raise ValueError("installation_id is required")
        t = TokenExpiry(token_id=token_id, label=label, expires_at=expires_at)
        self._tokens[(installation_id, token_id)] = t
        return t

    def expiring_soon(self, installation_id: str, within_days: int = 30) -> list[TokenExpiry]:
        threshold = time.time() + (within_days * 86400)
        now = time.time()
        return [
            t for (inst, _), t in self._tokens.items()
            if inst == installation_id and now < t.expires_at <= threshold
        ]

    def expired(self, installation_id: str) -> list[TokenExpiry]:
        return [t for (inst, _), t in self._tokens.items() if inst == installation_id and t.is_expired]

    def list_tokens(self, installation_id: str) -> list[TokenExpiry]:
        return [t for (inst, _), t in self._tokens.items() if inst == installation_id]
