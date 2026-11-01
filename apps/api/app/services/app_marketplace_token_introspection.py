"""Token Introspection — inspect and validate OAuth/API tokens.

Provides RFC 7662-style token introspection for validating access
tokens, checking scopes, and retrieving token metadata.
"""
from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class TokenInfo:
    token_hash: str
    client_id: str
    user_id: str
    scopes: list[str]
    issued_at: float
    expires_at: float
    token_type: str = "bearer"
    active: bool = True
    revoked: bool = False
    metadata: dict = field(default_factory=dict)


class TokenIntrospectionService:
    """RFC 7662-style token introspection."""

    def __init__(self):
        self._tokens: dict[str, TokenInfo] = {}

    def register_token(self, token: str, client_id: str, user_id: str,
                       scopes: list[str], ttl_seconds: int = 3600,
                       metadata: dict | None = None) -> TokenInfo:
        """Register a token for introspection."""
        now = time.time()
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        info = TokenInfo(
            token_hash=token_hash, client_id=client_id, user_id=user_id,
            scopes=scopes, issued_at=now, expires_at=now + ttl_seconds,
            metadata=metadata or {},
        )
        self._tokens[token_hash] = info
        return info

    def introspect(self, token: str) -> dict:
        """Introspect a token. Returns RFC 7662 response."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        info = self._tokens.get(token_hash)

        if not info:
            return {"active": False}

        if info.revoked:
            return {"active": False, "reason": "revoked"}

        if time.time() > info.expires_at:
            info.active = False
            return {"active": False, "reason": "expired"}

        return {
            "active": True,
            "scope": " ".join(info.scopes),
            "client_id": info.client_id,
            "sub": info.user_id,
            "token_type": info.token_type,
            "exp": int(info.expires_at),
            "iat": int(info.issued_at),
            **info.metadata,
        }

    def revoke(self, token: str) -> bool:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        info = self._tokens.get(token_hash)
        if info:
            info.revoked = True
            info.active = False
            return True
        return False

    def has_scope(self, token: str, required_scope: str) -> bool:
        """Check if token has a specific scope."""
        result = self.introspect(token)
        if not result.get("active"):
            return False
        scopes = result.get("scope", "").split()
        return required_scope in scopes or "*" in scopes

    def get_active_count(self, client_id: str | None = None) -> int:
        now = time.time()
        tokens = self._tokens.values()
        if client_id:
            tokens = [t for t in tokens if t.client_id == client_id]
        return sum(1 for t in tokens if t.active and not t.revoked and t.expires_at > now)
