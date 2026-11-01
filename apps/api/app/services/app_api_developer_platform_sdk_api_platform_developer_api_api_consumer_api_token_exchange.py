"""API Consumer Token Exchange — exchange authorization codes for access tokens."""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class AuthCode:
    code_id: str
    consumer_id: str
    code_hash: str
    scopes: list[str] = field(default_factory=list)
    redirect_uri: str = ""
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    used: bool = False

@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int
    scopes: list[str]

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTokenExchange:
    def __init__(self, code_ttl_s: int = 600, token_ttl_s: int = 3600) -> None:
        self._codes: dict[tuple[str, str], AuthCode] = {}
        self._code_ttl = max(30, code_ttl_s)
        self._token_ttl = max(60, token_ttl_s)

    def generate_code(self, installation_id: str, consumer_id: str, scopes: list[str], redirect_uri: str = "") -> dict[str, str]:
        if not installation_id: raise ValueError("installation_id is required")
        raw_code = secrets.token_urlsafe(32)
        code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
        now = time.time()
        ac = AuthCode(code_id=f"ac-{secrets.token_hex(8)}", consumer_id=consumer_id, code_hash=code_hash, scopes=scopes, redirect_uri=redirect_uri, expires_at=now + self._code_ttl)
        self._codes[(installation_id, ac.code_id)] = ac
        return {"code": raw_code, "code_id": ac.code_id}

    def exchange(self, installation_id: str, code_id: str, raw_code: str, redirect_uri: str = "") -> TokenPair:
        key = (installation_id, code_id)
        ac = self._codes.get(key)
        if ac is None: raise KeyError("Invalid authorization code")
        if ac.used: raise ValueError("Code already used")
        if time.time() > ac.expires_at: raise ValueError("Code expired")
        if hashlib.sha256(raw_code.encode()).hexdigest() != ac.code_hash: raise ValueError("Invalid code")
        if ac.redirect_uri and ac.redirect_uri != redirect_uri: raise ValueError("Redirect URI mismatch")
        ac.used = True
        return TokenPair(access_token=secrets.token_urlsafe(32), refresh_token=secrets.token_urlsafe(48), expires_in=self._token_ttl, scopes=ac.scopes)

    def pending_codes(self, installation_id: str) -> int:
        now = time.time()
        return sum(1 for (inst, _), ac in self._codes.items() if inst == installation_id and not ac.used and ac.expires_at > now)
