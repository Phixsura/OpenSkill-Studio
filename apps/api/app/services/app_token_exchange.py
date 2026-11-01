"""App Token Exchange — exchange authorization codes for access tokens.

Manages OAuth-style token exchange for installed apps:
- Issue authorization codes with expiry
- Exchange codes for access tokens
- Refresh token rotation
- Per-installation scoped tokens
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class AuthCode:
    """An authorization code."""

    code: str
    installation_id: str
    user_id: str
    scopes: list[str]
    created_at: float
    expires_at: float
    exchanged: bool = False


@dataclass
class TokenPair:
    """An access/refresh token pair."""

    access_token: str
    refresh_token: str
    installation_id: str
    user_id: str
    scopes: list[str]
    issued_at: float
    expires_at: float
    revoked: bool = False


class AppTokenExchange:
    """Exchange authorization codes for access tokens."""

    def __init__(
        self,
        code_ttl_seconds: int = 600,
        access_ttl_seconds: int = 3600,
    ) -> None:
        self._code_ttl = code_ttl_seconds
        self._access_ttl = access_ttl_seconds
        self._codes: dict[str, AuthCode] = {}
        self._tokens: dict[str, TokenPair] = {}  # access_token → TokenPair
        self._refresh_index: dict[str, str] = {}  # refresh_token → access_token

    def issue_code(
        self,
        installation_id: str,
        user_id: str,
        scopes: list[str] | None = None,
        now: float | None = None,
    ) -> AuthCode:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not user_id:
            raise ValueError("user_id is required")

        now = now or time.time()
        code = secrets.token_urlsafe(32)
        auth_code = AuthCode(
            code=code, installation_id=installation_id,
            user_id=user_id, scopes=scopes or [],
            created_at=now, expires_at=now + self._code_ttl,
        )
        self._codes[code] = auth_code
        return auth_code

    def exchange_code(
        self, code: str, installation_id: str, now: float | None = None
    ) -> TokenPair:
        """Exchange an auth code for a token pair."""
        now = now or time.time()
        auth_code = self._codes.get(code)
        if auth_code is None:
            raise KeyError("Invalid authorization code")
        if auth_code.installation_id != installation_id:
            raise PermissionError("Code not issued for this installation")
        if auth_code.exchanged:
            raise ValueError("Code already exchanged")
        if now >= auth_code.expires_at:
            raise ValueError("Code expired")

        auth_code.exchanged = True

        access = secrets.token_urlsafe(32)
        refresh = secrets.token_urlsafe(32)
        pair = TokenPair(
            access_token=access, refresh_token=refresh,
            installation_id=installation_id, user_id=auth_code.user_id,
            scopes=auth_code.scopes, issued_at=now,
            expires_at=now + self._access_ttl,
        )
        self._tokens[access] = pair
        self._refresh_index[refresh] = access
        return pair

    def refresh(self, refresh_token: str, now: float | None = None) -> TokenPair:
        """Rotate a refresh token for a new token pair."""
        now = now or time.time()
        old_access = self._refresh_index.get(refresh_token)
        if old_access is None:
            raise KeyError("Invalid refresh token")
        old_pair = self._tokens.get(old_access)
        if old_pair is None or old_pair.revoked:
            raise ValueError("Token revoked")

        # Revoke old pair
        old_pair.revoked = True
        del self._refresh_index[refresh_token]

        # Issue new pair
        access = secrets.token_urlsafe(32)
        new_refresh = secrets.token_urlsafe(32)
        pair = TokenPair(
            access_token=access, refresh_token=new_refresh,
            installation_id=old_pair.installation_id,
            user_id=old_pair.user_id, scopes=old_pair.scopes,
            issued_at=now, expires_at=now + self._access_ttl,
        )
        self._tokens[access] = pair
        self._refresh_index[new_refresh] = access
        return pair

    def validate_token(self, access_token: str, now: float | None = None) -> TokenPair | None:
        """Validate an access token. Returns None if invalid."""
        now = now or time.time()
        pair = self._tokens.get(access_token)
        if pair is None or pair.revoked or now >= pair.expires_at:
            return None
        return pair

    def revoke_token(self, access_token: str) -> None:
        pair = self._tokens.get(access_token)
        if pair:
            pair.revoked = True
