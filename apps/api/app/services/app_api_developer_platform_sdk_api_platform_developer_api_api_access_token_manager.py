"""API Access Token Manager — manage short-lived access tokens with refresh."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import secrets
import time
import structlog

log = structlog.get_logger()

@dataclass
class AccessToken:
    token_id: str
    consumer_id: str
    scopes: list[str] = field(default_factory=list)
    issued_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    revoked: bool = False
    token_hash: str = ""  # SHA-256 of actual token

@dataclass
class RefreshToken:
    refresh_id: str
    consumer_id: str
    token_hash: str = ""
    issued_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    used: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAccessTokenManager:
    def __init__(self, access_ttl_s: int = 3600, refresh_ttl_s: int = 86400) -> None:
        self._access: dict[tuple[str, str], AccessToken] = {}
        self._refresh: dict[tuple[str, str], RefreshToken] = {}
        self._access_ttl = max(60, access_ttl_s)
        self._refresh_ttl = max(3600, refresh_ttl_s)

    def issue(self, installation_id: str, consumer_id: str, scopes: list[str]) -> dict[str, str]:
        if not installation_id: raise ValueError("installation_id is required")
        now = time.time()
        raw_access = secrets.token_urlsafe(32)
        raw_refresh = secrets.token_urlsafe(48)
        access_hash = hashlib.sha256(raw_access.encode()).hexdigest()
        refresh_hash = hashlib.sha256(raw_refresh.encode()).hexdigest()
        token_id = f"at-{secrets.token_hex(8)}"
        refresh_id = f"rt-{secrets.token_hex(8)}"
        at = AccessToken(token_id=token_id, consumer_id=consumer_id, scopes=scopes, issued_at=now, expires_at=now + self._access_ttl, token_hash=access_hash)
        rt = RefreshToken(refresh_id=refresh_id, consumer_id=consumer_id, token_hash=refresh_hash, issued_at=now, expires_at=now + self._refresh_ttl)
        self._access[(installation_id, token_id)] = at
        self._refresh[(installation_id, refresh_id)] = rt
        return {"access_token": raw_access, "refresh_token": raw_refresh, "token_id": token_id, "refresh_id": refresh_id, "expires_in": self._access_ttl}

    def validate(self, installation_id: str, token_id: str, raw_token: str) -> AccessToken | None:
        at = self._access.get((installation_id, token_id))
        if at is None: return None
        if at.revoked: return None
        if at.expires_at < time.time(): return None
        if hashlib.sha256(raw_token.encode()).hexdigest() != at.token_hash: return None
        return at

    def revoke(self, installation_id: str, token_id: str) -> bool:
        at = self._access.get((installation_id, token_id))
        if at: at.revoked = True; return True
        return False

    def active_token_count(self, installation_id: str) -> int:
        now = time.time()
        return sum(1 for (inst, _), at in self._access.items() if inst == installation_id and not at.revoked and at.expires_at > now)

    def list_tokens(self, installation_id: str, consumer_id: str) -> list[AccessToken]:
        return [at for (inst, _), at in self._access.items() if inst == installation_id and at.consumer_id == consumer_id]
