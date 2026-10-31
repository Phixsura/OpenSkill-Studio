"""Consumer API Token Rotation — manage token lifecycle with grace periods."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import secrets
import structlog

log = structlog.get_logger()

@dataclass
class APIToken:
    token_id: str
    consumer_id: str
    token_hash: str  # store only hash
    created_at: datetime
    expires_at: datetime
    revoked: bool = False
    predecessor_id: str | None = None  # previous token this replaced

@dataclass
class RotationResult:
    new_token: str  # plaintext, returned only once
    new_token_id: str
    old_token_id: str
    grace_until: datetime

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiTokenRotation:
    def __init__(self, grace_period_hours: int = 24) -> None:
        self._tokens: dict[tuple[str, str], APIToken] = {}  # (inst, token_id)
        self._grace_hours = grace_period_hours

    def issue(self, installation_id: str, consumer_id: str, ttl_days: int = 90, now: datetime | None = None) -> tuple[str, APIToken]:
        if not installation_id:
            raise ValueError("installation_id is required")
        now = now or datetime.utcnow()
        raw = secrets.token_urlsafe(32)
        token_id = hashlib.sha256(raw.encode()).hexdigest()[:16]
        token = APIToken(token_id=token_id, consumer_id=consumer_id, token_hash=hashlib.sha256(raw.encode()).hexdigest(), created_at=now, expires_at=now + timedelta(days=ttl_days))
        self._tokens[(installation_id, token_id)] = token
        log.info("token_issued", installation_id=installation_id, consumer_id=consumer_id, token_id=token_id)
        return raw, token

    def rotate(self, installation_id: str, consumer_id: str, old_token_id: str, now: datetime | None = None) -> RotationResult:
        now = now or datetime.utcnow()
        old_key = (installation_id, old_token_id)
        old_token = self._tokens.get(old_key)
        if not old_token:
            raise ValueError("Token not found")
        if old_token.consumer_id != consumer_id:
            raise ValueError("Token does not belong to consumer")
        raw, new_token = self.issue(installation_id, consumer_id, now=now)
        new_token.predecessor_id = old_token_id
        grace_until = now + timedelta(hours=self._grace_hours)
        return RotationResult(new_token=raw, new_token_id=new_token.token_id, old_token_id=old_token_id, grace_until=grace_until)

    def revoke(self, installation_id: str, token_id: str) -> APIToken:
        key = (installation_id, token_id)
        token = self._tokens.get(key)
        if not token:
            raise ValueError("Token not found")
        token.revoked = True
        return token

    def validate(self, installation_id: str, token_hash: str, now: datetime | None = None) -> APIToken | None:
        now = now or datetime.utcnow()
        for (inst, _), t in self._tokens.items():
            if inst == installation_id and t.token_hash == token_hash and not t.revoked and now < t.expires_at:
                return t
        return None

    def list_tokens(self, installation_id: str, consumer_id: str) -> list[APIToken]:
        return [t for (inst, _), t in self._tokens.items() if inst == installation_id and t.consumer_id == consumer_id]
