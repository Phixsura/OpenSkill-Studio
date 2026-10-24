"""Token introspection — inspect and validate API tokens with scope details."""

import hashlib
import time


def introspect_token(*, token_hash: str, stored_tokens: dict[str, dict]) -> dict:
    token_data = stored_tokens.get(token_hash)
    if not token_data:
        return {"active": False, "error": "Token not found"}
    now = int(time.time())
    expired = token_data.get("expires_at", 0) > 0 and now > token_data["expires_at"]
    revoked = token_data.get("revoked", False)
    return {
        "active": not expired and not revoked,
        "app_id": token_data.get("app_id"),
        "scopes": token_data.get("scopes", []),
        "issued_at": token_data.get("issued_at"),
        "expires_at": token_data.get("expires_at"),
        "expired": expired, "revoked": revoked,
    }


def check_token_scope(*, token_scopes: list[str], required_scope: str) -> dict:
    has_scope = required_scope in token_scopes or "admin" in token_scopes
    return {"authorized": has_scope, "required": required_scope,
            "granted": token_scopes, "missing": [] if has_scope else [required_scope]}


def compute_token_usage_stats(*, tokens: list[dict]) -> dict:
    active = sum(1 for t in tokens if t.get("active"))
    expired = sum(1 for t in tokens if t.get("expired"))
    revoked = sum(1 for t in tokens if t.get("revoked"))
    return {"total": len(tokens), "active": active, "expired": expired, "revoked": revoked}
