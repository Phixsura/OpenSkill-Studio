"""API key manager — create, list, revoke API keys."""

import secrets
import hashlib
import html
from datetime import datetime, timezone


def create_api_key(*, name: str, scopes: list[str]) -> dict:
    raw = f"osk_{secrets.token_hex(24)}"
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    return {"key": raw, "key_hash": key_hash, "prefix": raw[:8],
            "name": html.escape(name), "scopes": scopes,
            "created_at": datetime.now(timezone.utc).isoformat()}


def list_api_keys(*, keys: list[dict]) -> dict:
    items = [{"prefix": k["prefix"], "name": html.escape(k.get("name", "")),
              "scopes": k.get("scopes", []), "created_at": k.get("created_at"),
              "revoked": k.get("revoked", False)} for k in keys]
    return {"keys": items, "total": len(items),
            "active": sum(1 for k in items if not k["revoked"])}


def revoke_api_key(*, keys: list[dict], prefix: str) -> dict:
    for k in keys:
        if k["prefix"] == prefix and not k.get("revoked"):
            k["revoked"] = True
            return {"revoked": True, "prefix": prefix}
    return {"revoked": False, "error": "Key not found or already revoked"}
