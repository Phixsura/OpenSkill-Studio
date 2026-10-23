"""API key display — safe display formatting for API keys with masking."""
from __future__ import annotations
import secrets
import time


def generate_api_key(*, prefix: str = "sk_live", length: int = 32) -> dict:
    raw = secrets.token_urlsafe(length)
    key = f"{prefix}_{raw}"
    return {"key": key, "prefix": prefix, "created_at": time.time(),
            "display": mask_key(key), "full_length": len(key)}


def mask_key(key: str, *, show_chars: int = 8) -> str:
    if len(key) <= show_chars:
        return "•" * len(key)
    return key[:show_chars] + "•" * (len(key) - show_chars)


def format_key_list(keys: list[dict]) -> list[dict]:
    return [{"name": k.get("name", ""), "prefix": k.get("key", "")[:8],
             "masked": mask_key(k.get("key", "")),
             "created": k.get("created", ""), "last_used": k.get("last_used", "never"),
             "scopes": k.get("scopes", [])} for k in keys]
