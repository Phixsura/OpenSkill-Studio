"""Token Introspector — OAuth2 token introspection (RFC 7662).

Implements:
- Store tokens with metadata (scopes, subject, expiry)
- Introspect: return active/inactive + metadata
- Revocation marking
- Client-bound tokens (only issuing client can introspect)
- Token type detection (access_token, refresh_token)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import secrets


@dataclass
class TokenRecord:
    token: str
    token_type: str  # access_token, refresh_token
    active: bool = True
    subject: str = ""
    client_id: str = ""
    scopes: list[str] = field(default_factory=list)
    issued_at: float = 0.0
    expires_at: float = 0.0
    revoked_at: float = 0.0

    def __post_init__(self):
        if not self.issued_at: self.issued_at = time.time()


class TokenIntrospectorService:
    def __init__(self):
        self._tokens: dict[str, TokenRecord] = {}

    def issue(self, subject: str, client_id: str, scopes: list[str],
              token_type: str = "access_token",
              ttl_seconds: float = 3600) -> TokenRecord:
        """Issue a new token."""
        token = secrets.token_urlsafe(32)
        now = time.time()
        record = TokenRecord(
            token=token, token_type=token_type, subject=subject,
            client_id=client_id, scopes=scopes,
            issued_at=now, expires_at=now + ttl_seconds)
        self._tokens[token] = record
        return record

    def introspect(self, token: str, client_id: str = "") -> dict:
        """RFC 7662 introspection response."""
        record = self._tokens.get(token)
        if not record:
            return {"active": False}

        now = time.time()

        # Check if revoked
        if record.revoked_at > 0:
            return {"active": False}

        # Check expiry
        if record.expires_at > 0 and now > record.expires_at:
            return {"active": False}

        # Client binding (optional): only issuing client can introspect
        if client_id and record.client_id != client_id:
            return {"active": False}

        return {
            "active": True,
            "scope": " ".join(record.scopes),
            "client_id": record.client_id,
            "sub": record.subject,
            "token_type": record.token_type,
            "exp": int(record.expires_at),
            "iat": int(record.issued_at),
            "nbf": int(record.issued_at),
        }

    def revoke(self, token: str, client_id: str = "") -> bool:
        """Revoke a token."""
        record = self._tokens.get(token)
        if not record:
            return False
        if client_id and record.client_id != client_id:
            return False
        record.active = False
        record.revoked_at = time.time()
        return True

    def revoke_by_subject(self, subject: str) -> int:
        """Revoke all tokens for a subject (e.g., user logout)."""
        count = 0
        for record in self._tokens.values():
            if record.subject == subject and record.revoked_at == 0:
                record.active = False
                record.revoked_at = time.time()
                count += 1
        return count

    def cleanup_expired(self) -> int:
        """Remove expired/revoked tokens from store."""
        now = time.time()
        to_remove = [t for t, r in self._tokens.items()
                     if (r.expires_at > 0 and now > r.expires_at + 86400) or
                     r.revoked_at > 0]
        for t in to_remove:
            del self._tokens[t]
        return len(to_remove)

    def stats(self) -> dict:
        now = time.time()
        active = sum(1 for r in self._tokens.values()
                     if r.revoked_at == 0 and r.expires_at > now)
        return {"total": len(self._tokens), "active": active}
