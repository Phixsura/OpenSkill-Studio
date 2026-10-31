"""API Token Introspection — token metadata inspection with expiry checks."""
from __future__ import annotations

import secrets
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class TokenInfo:
    token_id: str
    consumer_id: str
    token_type: str  # access, refresh, api_key
    scopes: list[str] = field(default_factory=list)
    issued_at: float = 0.0
    expires_at: float = 0.0
    revoked: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class TokenIntrospection:
    """Inspect token metadata, validate expiry, and check revocation."""

    _tokens: dict[str, TokenInfo] = field(default_factory=dict)
    _token_to_id: dict[str, str] = field(default_factory=dict)  # opaque token -> token_id

    def issue(self, consumer_id: str, token_type: str = "access",
              scopes: list[str] | None = None, issued_at: float = 0.0,
              ttl_seconds: float = 3600.0) -> dict:
        if token_type not in ("access", "refresh", "api_key"):
            raise ValueError(f"Invalid token type: {token_type}")
        token_id = f"tok_{secrets.token_hex(8)}"
        opaque = secrets.token_hex(32)
        expires = issued_at + ttl_seconds if ttl_seconds > 0 else 0.0
        info = TokenInfo(
            token_id=token_id, consumer_id=consumer_id,
            token_type=token_type, scopes=scopes or [],
            issued_at=issued_at, expires_at=expires,
        )
        self._tokens[token_id] = info
        self._token_to_id[opaque] = token_id
        logger.info("token_issued", token_id=token_id, type=token_type)
        return {"token_id": token_id, "token": opaque, "expires_at": expires}

    def introspect(self, token: str, current_time: float = 0.0) -> dict:
        token_id = self._token_to_id.get(token)
        if not token_id:
            return {"active": False, "reason": "unknown_token"}
        info = self._tokens.get(token_id)
        if not info:
            return {"active": False, "reason": "token_deleted"}
        if info.revoked:
            return {"active": False, "reason": "revoked", "token_id": token_id}
        if info.expires_at > 0 and current_time > info.expires_at:
            return {"active": False, "reason": "expired", "token_id": token_id,
                    "expired_seconds_ago": round(current_time - info.expires_at, 1)}
        remaining = info.expires_at - current_time if info.expires_at > 0 else None
        return {
            "active": True,
            "token_id": token_id,
            "consumer_id": info.consumer_id,
            "token_type": info.token_type,
            "scopes": info.scopes,
            "issued_at": info.issued_at,
            "expires_at": info.expires_at,
            "remaining_seconds": round(remaining, 1) if remaining else None,
        }

    def revoke(self, token_id: str) -> dict:
        info = self._tokens.get(token_id)
        if not info:
            return {"revoked": False, "reason": "not_found"}
        info.revoked = True
        logger.info("token_revoked", token_id=token_id)
        return {"revoked": True, "token_id": token_id}

    def revoke_all(self, consumer_id: str) -> dict:
        count = 0
        for info in self._tokens.values():
            if info.consumer_id == consumer_id and not info.revoked:
                info.revoked = True
                count += 1
        return {"consumer_id": consumer_id, "revoked_count": count}

    def list_tokens(self, consumer_id: str) -> list[dict]:
        return [
            {"token_id": t.token_id, "type": t.token_type,
             "scopes": t.scopes, "revoked": t.revoked,
             "expires_at": t.expires_at}
            for t in self._tokens.values() if t.consumer_id == consumer_id
        ]

    def get_stats(self) -> dict:
        all_tokens = list(self._tokens.values())
        return {
            "total_tokens": len(all_tokens),
            "active": sum(1 for t in all_tokens if not t.revoked),
            "revoked": sum(1 for t in all_tokens if t.revoked),
            "by_type": {
                tt: sum(1 for t in all_tokens if t.token_type == tt)
                for tt in ("access", "refresh", "api_key")
            },
        }
