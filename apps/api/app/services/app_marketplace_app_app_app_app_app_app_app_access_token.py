"""Access token manager — issue, validate, and revoke platform tokens."""
from __future__ import annotations
import secrets, hashlib, time


class AccessTokenManager:
    def __init__(self, ttl_seconds: int = 3600):
        self._tokens: dict[str, dict] = {}
        self._ttl = ttl_seconds
        self._revoked: set[str] = set()

    def issue(self, subject: str, scopes: list[str]) -> dict:
        token = f"osk_{secrets.token_urlsafe(32)}"
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self._tokens[token_hash] = {"subject": subject, "scopes": scopes,
                                     "issued_at": time.time(),
                                     "expires_at": time.time() + self._ttl}
        return {"token": token, "token_hash": token_hash[:12],
                "expires_in": self._ttl, "scopes": scopes}

    def validate(self, token: str, now: float | None = None) -> dict:
        now = now or time.time()
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if token_hash in self._revoked:
            return {"valid": False, "reason": "revoked"}
        entry = self._tokens.get(token_hash)
        if not entry:
            return {"valid": False, "reason": "not_found"}
        if now > entry["expires_at"]:
            return {"valid": False, "reason": "expired"}
        return {"valid": True, "subject": entry["subject"], "scopes": entry["scopes"]}

    def revoke(self, token: str) -> dict:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self._revoked.add(token_hash)
        return {"revoked": True}

    def stats(self) -> dict:
        return {"active": len(self._tokens), "revoked": len(self._revoked)}
