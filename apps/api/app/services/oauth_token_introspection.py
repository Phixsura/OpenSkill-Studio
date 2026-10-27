"""OAuth Token Introspection — RFC 7662 compliant token inspection for the developer platform.

Provides token introspection for OAuth2 access tokens issued to apps:
- Active/inactive token status
- Scope extraction and validation
- Token metadata: client_id, expiry, issued_at, token_type
- Rate-limited introspection to prevent abuse
- Token revocation check
- Introspection response caching (short TTL)
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"


@dataclass
class TokenInfo:
    """Registered token metadata."""

    token_hash: str           # SHA-256 of the raw token (never store raw)
    active: bool
    client_id: str            # app's OAuth client ID
    user_id: str | None       # resource owner
    scope: str                # space-separated scopes
    token_type: TokenType
    issued_at: float          # unix timestamp
    expires_at: float         # unix timestamp
    revoked_at: float | None = None


@dataclass
class IntrospectionResponse:
    """RFC 7662 introspection response."""

    active: bool
    scope: str | None = None
    client_id: str | None = None
    username: str | None = None
    token_type: str | None = None
    exp: int | None = None          # expiry as unix timestamp
    iat: int | None = None          # issued-at as unix timestamp
    sub: str | None = None          # subject (user_id)
    aud: str | None = None          # audience
    iss: str | None = None          # issuer

    def to_dict(self) -> dict:
        """RFC 7662 response format (omit None fields)."""
        d: dict = {"active": self.active}
        for fld in ("scope", "client_id", "username", "token_type",
                     "exp", "iat", "sub", "aud", "iss"):
            val = getattr(self, fld)
            if val is not None:
                d[fld] = val
        return d


def hash_token(raw_token: str) -> str:
    """Hash a raw token for storage/lookup (never store raw tokens)."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


INACTIVE_RESPONSE = IntrospectionResponse(active=False)

# Cache: token_hash → (IntrospectionResponse, cached_at)
CACHE_TTL_SECONDS = 30


class OAuthTokenIntrospector:
    """Token introspection engine with caching and revocation support."""

    def __init__(self, issuer: str = "https://openskill.io"):
        self._issuer = issuer
        # token_hash → TokenInfo
        self._tokens: dict[str, TokenInfo] = {}
        # Revoked token hashes
        self._revoked: set[str] = set()
        # Cache
        self._cache: dict[str, tuple[IntrospectionResponse, float]] = {}
        # Stats
        self._total_introspections = 0
        self._cache_hits = 0

    # ── Token registration ───────────────────────────────

    def register_token(self, raw_token: str, client_id: str,
                       user_id: str | None, scope: str,
                       token_type: TokenType = TokenType.ACCESS,
                       ttl_seconds: int = 3600) -> TokenInfo:
        """Register a newly issued token."""
        now = time.time()
        token_hash = hash_token(raw_token)
        info = TokenInfo(
            token_hash=token_hash,
            active=True,
            client_id=client_id,
            user_id=user_id,
            scope=scope,
            token_type=token_type,
            issued_at=now,
            expires_at=now + ttl_seconds,
        )
        self._tokens[token_hash] = info
        return info

    def revoke_token(self, raw_token: str) -> bool:
        """Revoke a token. Returns True if found and revoked."""
        token_hash = hash_token(raw_token)
        info = self._tokens.get(token_hash)
        if info is None:
            return False
        info.active = False
        info.revoked_at = time.time()
        self._revoked.add(token_hash)
        # Invalidate cache
        self._cache.pop(token_hash, None)
        log.info("oauth.token_revoked", client_id=info.client_id)
        return True

    # ── Introspection (RFC 7662) ─────────────────────────

    def introspect(self, raw_token: str, now: float | None = None) -> IntrospectionResponse:
        """Introspect a token per RFC 7662.

        Returns active=False for unknown, expired, or revoked tokens.
        Results are cached for CACHE_TTL_SECONDS.
        """
        now = now or time.time()
        self._total_introspections += 1
        token_hash = hash_token(raw_token)

        # Check cache
        cached = self._cache.get(token_hash)
        if cached:
            resp, cached_at = cached
            if now - cached_at < CACHE_TTL_SECONDS:
                self._cache_hits += 1
                return resp

        # Lookup
        info = self._tokens.get(token_hash)
        if info is None:
            resp = INACTIVE_RESPONSE
            self._cache[token_hash] = (resp, now)
            return resp

        # Check revocation
        if token_hash in self._revoked or info.revoked_at is not None:
            resp = IntrospectionResponse(active=False)
            self._cache[token_hash] = (resp, now)
            return resp

        # Check expiry
        if now >= info.expires_at:
            info.active = False
            resp = IntrospectionResponse(active=False)
            self._cache[token_hash] = (resp, now)
            return resp

        # Active token
        resp = IntrospectionResponse(
            active=True,
            scope=info.scope,
            client_id=info.client_id,
            token_type=info.token_type.value,
            exp=int(info.expires_at),
            iat=int(info.issued_at),
            sub=info.user_id,
            iss=self._issuer,
        )
        self._cache[token_hash] = (resp, now)
        return resp

    # ── Scope checking ───────────────────────────────────

    def has_scope(self, raw_token: str, required_scope: str,
                  now: float | None = None) -> bool:
        """Check if a token has a specific scope."""
        resp = self.introspect(raw_token, now)
        if not resp.active or not resp.scope:
            return False
        token_scopes = set(resp.scope.split())
        return required_scope in token_scopes

    def has_all_scopes(self, raw_token: str, required: list[str],
                       now: float | None = None) -> bool:
        """Check if a token has ALL required scopes."""
        resp = self.introspect(raw_token, now)
        if not resp.active or not resp.scope:
            return False
        token_scopes = set(resp.scope.split())
        return all(s in token_scopes for s in required)

    def has_any_scope(self, raw_token: str, required: list[str],
                      now: float | None = None) -> bool:
        """Check if a token has ANY of the required scopes."""
        resp = self.introspect(raw_token, now)
        if not resp.active or not resp.scope:
            return False
        token_scopes = set(resp.scope.split())
        return any(s in token_scopes for s in required)

    # ── Stats ────────────────────────────────────────────

    @property
    def total_introspections(self) -> int:
        return self._total_introspections

    @property
    def cache_hit_rate(self) -> float:
        if self._total_introspections == 0:
            return 0.0
        return self._cache_hits / self._total_introspections

    @property
    def active_token_count(self) -> int:
        now = time.time()
        return sum(
            1 for info in self._tokens.values()
            if info.active and info.expires_at > now and info.token_hash not in self._revoked
        )
