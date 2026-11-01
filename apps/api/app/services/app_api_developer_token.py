"""App API Developer Token — manage personal access tokens for developers."""
from __future__ import annotations
import hashlib, secrets, time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeveloperToken:
    token_id: str
    developer_id: str
    name: str
    prefix: str
    token_hash: str
    scopes: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_used_at: float | None = None
    revoked: bool = False

class AppAPIDeveloperToken:
    def __init__(self) -> None:
        self._tokens: dict[tuple[str, str], DeveloperToken] = {}

    def create(self, installation_id: str, token_id: str, developer_id: str, name: str, scopes: list[str] | None = None) -> tuple[DeveloperToken, str]:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, token_id)
        if key in self._tokens: raise ValueError(f"Token {token_id} already exists")
        raw = secrets.token_urlsafe(32)
        t = DeveloperToken(token_id=token_id, developer_id=developer_id, name=name, prefix=raw[:8], token_hash=hashlib.sha256(raw.encode()).hexdigest(), scopes=scopes or [])
        self._tokens[key] = t
        return t, raw

    def validate(self, installation_id: str, raw_token: str) -> DeveloperToken | None:
        h = hashlib.sha256(raw_token.encode()).hexdigest()
        for (inst, _), t in self._tokens.items():
            if inst == installation_id and t.token_hash == h and not t.revoked:
                t.last_used_at = time.time()
                return t
        return None

    def revoke(self, installation_id: str, token_id: str) -> DeveloperToken:
        t = self._tokens.get((installation_id, token_id))
        if t is None: raise KeyError(f"Token {token_id} not found")
        t.revoked = True
        return t

    def list_tokens(self, installation_id: str, developer_id: str | None = None) -> list[DeveloperToken]:
        tokens = [t for (inst, _), t in self._tokens.items() if inst == installation_id]
        if developer_id: tokens = [t for t in tokens if t.developer_id == developer_id]
        return tokens
