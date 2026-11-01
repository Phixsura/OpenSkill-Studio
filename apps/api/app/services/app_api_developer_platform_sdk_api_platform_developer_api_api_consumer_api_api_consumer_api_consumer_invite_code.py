"""Consumer Invite Code — generate and redeem invitation codes for API access."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class InviteCode:
    code: str
    created_by: str
    plan_id: str | None = None
    max_uses: int = 1
    used_count: int = 0
    expires_at: datetime | None = None
    created_at: datetime | None = None
    disabled: bool = False

@dataclass
class RedemptionResult:
    success: bool
    code: str
    consumer_id: str | None = None
    reason: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerInviteCode:
    def __init__(self) -> None:
        self._codes: dict[tuple[str, str], InviteCode] = {}
        self._redemptions: dict[tuple[str, str], list[str]] = {}  # code -> [consumer_ids]

    def generate(self, installation_id: str, created_by: str, plan_id: str | None = None, max_uses: int = 1, ttl_days: int = 7, now: datetime | None = None) -> InviteCode:
        if not installation_id:
            raise ValueError("installation_id is required")
        if max_uses < 1:
            raise ValueError("max_uses must be positive")
        now = now or datetime.utcnow()
        raw = f"{installation_id}:{created_by}:{now.isoformat()}"
        code = hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
        invite = InviteCode(code=code, created_by=created_by, plan_id=plan_id, max_uses=max_uses, expires_at=now + timedelta(days=ttl_days), created_at=now)
        self._codes[(installation_id, code)] = invite
        log.info("invite_generated", installation_id=installation_id, code=code)
        return invite

    def redeem(self, installation_id: str, code: str, consumer_id: str, now: datetime | None = None) -> RedemptionResult:
        now = now or datetime.utcnow()
        key = (installation_id, code)
        invite = self._codes.get(key)
        if not invite:
            return RedemptionResult(success=False, code=code, reason="code_not_found")
        if invite.disabled:
            return RedemptionResult(success=False, code=code, reason="code_disabled")
        if invite.expires_at and now >= invite.expires_at:
            return RedemptionResult(success=False, code=code, reason="code_expired")
        if invite.used_count >= invite.max_uses:
            return RedemptionResult(success=False, code=code, reason="max_uses_reached")
        # Check duplicate redemption
        redeemed = self._redemptions.get(key, [])
        if consumer_id in redeemed:
            return RedemptionResult(success=False, code=code, reason="already_redeemed")
        invite.used_count += 1
        redeemed.append(consumer_id)
        self._redemptions[key] = redeemed
        return RedemptionResult(success=True, code=code, consumer_id=consumer_id)

    def disable(self, installation_id: str, code: str) -> InviteCode:
        key = (installation_id, code)
        invite = self._codes.get(key)
        if not invite:
            raise ValueError("Code not found")
        invite.disabled = True
        return invite

    def list_codes(self, installation_id: str) -> list[InviteCode]:
        return [c for (inst, _), c in self._codes.items() if inst == installation_id]
