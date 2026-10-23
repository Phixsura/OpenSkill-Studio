"""Access token manager — issue and validate short-lived tokens."""
from __future__ import annotations
import secrets
import hashlib
import time

_tokens: dict[str, dict] = {}


def issue_token(subject: str, scopes: list[str], ttl_sec: int = 3600) -> dict:
    raw = secrets.token_urlsafe(32)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    _tokens[hashed] = {"subject": subject, "scopes": scopes,
                        "issued_at": time.time(),
                        "expires_at": time.time() + ttl_sec,
                        "revoked": False}
    return {"token": raw, "subject": subject, "scopes": scopes,
            "expires_in": ttl_sec}


def validate_token(raw: str, required_scope: str | None = None) -> dict:
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    entry = _tokens.get(hashed)
    if not entry:
        return {"valid": False, "error": "not_found"}
    if entry["revoked"]:
        return {"valid": False, "error": "revoked"}
    if time.time() > entry["expires_at"]:
        return {"valid": False, "error": "expired"}
    if required_scope and required_scope not in entry["scopes"]:
        return {"valid": False, "error": "insufficient_scope"}
    return {"valid": True, "subject": entry["subject"], "scopes": entry["scopes"]}


def revoke_token(raw: str) -> dict:
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    if hashed in _tokens:
        _tokens[hashed]["revoked"] = True
        return {"revoked": True}
    return {"revoked": False, "error": "not_found"}


def clear_tokens() -> None:
    _tokens.clear()
