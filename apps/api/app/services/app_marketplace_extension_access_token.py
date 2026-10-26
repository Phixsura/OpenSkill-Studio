"""Access Token Manager — scoped, expiring tokens for extension API access.

Issues JWT-like access tokens with fine-grained scopes, expiration,
refresh flow, and revocation with an audit trail.
"""
from __future__ import annotations
import hashlib
import secrets
import time
from dataclasses import dataclass, field


VALID_SCOPES = {
    "read:data", "write:data", "read:config", "write:config",
    "read:users", "admin:extension", "webhook:manage", "analytics:read",
}


@dataclass
class AccessToken:
    token_id: str
    extension_id: str
    owner_id: str
    scopes: set[str]
    token_hash: str  # store hash, not raw token
    expires_at: float
    created_at: float
    revoked: bool = False
    last_used: float = 0.0
    use_count: int = 0


@dataclass
class RefreshToken:
    token_id: str
    access_token_id: str
    token_hash: str
    expires_at: float
    used: bool = False


class AccessTokenService:
    """Manages scoped access tokens with refresh and revocation."""

    TOKEN_TTL = 3600  # 1 hour
    REFRESH_TTL = 86400 * 30  # 30 days

    def __init__(self):
        self._tokens: dict[str, AccessToken] = {}
        self._refresh: dict[str, RefreshToken] = {}
        self._hash_index: dict[str, str] = {}  # token_hash -> token_id
        self._audit: list[dict] = []

    def _hash(self, raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    def issue(self, extension_id: str, owner_id: str,
              scopes: list[str], ttl: float | None = None) -> dict:
        for s in scopes:
            if s not in VALID_SCOPES:
                raise ValueError(f"Invalid scope: {s}")

        now = time.time()
        raw_token = f"ext_{secrets.token_urlsafe(32)}"
        raw_refresh = f"ref_{secrets.token_urlsafe(32)}"
        token_id = f"tok_{secrets.token_urlsafe(8)}"
        refresh_id = f"rtk_{secrets.token_urlsafe(8)}"

        t_hash = self._hash(raw_token)
        r_hash = self._hash(raw_refresh)

        token = AccessToken(
            token_id=token_id, extension_id=extension_id,
            owner_id=owner_id, scopes=set(scopes),
            token_hash=t_hash, expires_at=now + (ttl or self.TOKEN_TTL),
            created_at=now,
        )
        refresh = RefreshToken(
            token_id=refresh_id, access_token_id=token_id,
            token_hash=r_hash, expires_at=now + self.REFRESH_TTL,
        )

        self._tokens[token_id] = token
        self._refresh[refresh_id] = refresh
        self._hash_index[t_hash] = token_id
        self._audit.append({"action": "issue", "token_id": token_id,
                            "extension_id": extension_id, "time": now})

        return {
            "access_token": raw_token,
            "refresh_token": raw_refresh,
            "token_id": token_id,
            "expires_at": token.expires_at,
            "scopes": sorted(scopes),
        }

    def validate(self, raw_token: str) -> dict:
        t_hash = self._hash(raw_token)
        token_id = self._hash_index.get(t_hash)
        if not token_id:
            return {"valid": False, "reason": "Token not found"}

        token = self._tokens[token_id]
        if token.revoked:
            return {"valid": False, "reason": "Token revoked"}
        if time.time() > token.expires_at:
            return {"valid": False, "reason": "Token expired"}

        token.last_used = time.time()
        token.use_count += 1
        return {
            "valid": True, "token_id": token_id,
            "extension_id": token.extension_id,
            "scopes": sorted(token.scopes),
        }

    def check_scope(self, raw_token: str, required_scope: str) -> bool:
        result = self.validate(raw_token)
        if not result["valid"]:
            return False
        return required_scope in result["scopes"]

    def revoke(self, token_id: str) -> bool:
        token = self._tokens.get(token_id)
        if token and not token.revoked:
            token.revoked = True
            self._audit.append({"action": "revoke", "token_id": token_id,
                                "time": time.time()})
            return True
        return False

    def revoke_all(self, extension_id: str) -> int:
        count = 0
        for token in self._tokens.values():
            if token.extension_id == extension_id and not token.revoked:
                token.revoked = True
                count += 1
        return count

    def get_audit_log(self, extension_id: str) -> list[dict]:
        return [a for a in self._audit if a.get("extension_id") == extension_id]
