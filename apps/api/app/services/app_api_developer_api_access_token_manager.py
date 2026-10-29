"""App API Developer Access Token Manager — centralized token lifecycle management."""
from __future__ import annotations
import hashlib, secrets, time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class AccessToken:
    token_id: str
    developer_id: str
    name: str
    token_hash: str
    scopes: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    revoked: bool = False
    last_used_at: float | None = None
    use_count: int = 0

    @property
    def is_active(self) -> bool:
        if self.revoked: return False
        if self.expires_at and time.time() > self.expires_at: return False
        return True

class AppAPIDeveloperAPIAccessTokenManager:
    def __init__(self) -> None:
        self._tokens: dict[tuple[str, str], AccessToken] = {}

    def create(self, installation_id: str, token_id: str, developer_id: str, name: str, scopes: list[str] | None = None, ttl_seconds: int | None = None) -> tuple[AccessToken, str]:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, token_id)
        if key in self._tokens: raise ValueError(f"Token {token_id} exists")
        raw = secrets.token_urlsafe(32)
        expires_at = (time.time() + ttl_seconds) if ttl_seconds else None
        t = AccessToken(token_id=token_id, developer_id=developer_id, name=name, token_hash=hashlib.sha256(raw.encode()).hexdigest(), scopes=scopes or [], expires_at=expires_at)
        self._tokens[key] = t
        return t, raw

    def validate(self, installation_id: str, raw_token: str) -> AccessToken | None:
        h = hashlib.sha256(raw_token.encode()).hexdigest()
        for (inst, _), t in self._tokens.items():
            if inst == installation_id and t.token_hash == h and t.is_active:
                t.last_used_at = time.time()
                t.use_count += 1
                return t
        return None

    def revoke(self, installation_id: str, token_id: str) -> AccessToken:
        t = self._tokens.get((installation_id, token_id))
        if t is None: raise KeyError(f"Token {token_id} not found")
        t.revoked = True
        return t

    def active_tokens(self, installation_id: str, developer_id: str | None = None) -> list[AccessToken]:
        tokens = [t for (inst, _), t in self._tokens.items() if inst == installation_id and t.is_active]
        if developer_id: tokens = [t for t in tokens if t.developer_id == developer_id]
        return tokens

    def list_tokens(self, installation_id: str) -> list[AccessToken]:
        return [t for (inst, _), t in self._tokens.items() if inst == installation_id]
