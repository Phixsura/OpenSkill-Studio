"""App API keys page — app-level API key management page."""

import html
import secrets
from datetime import datetime, timezone


def build_keys_page(*, app_name: str, keys: list[dict]) -> dict:
    items = []
    active = 0
    for k in keys:
        is_active = not k.get("revoked", False)
        if is_active:
            active += 1
        items.append({
            "prefix": k.get("prefix", ""),
            "name": html.escape(k.get("name", "")),
            "scopes": k.get("scopes", []),
            "created_at": k.get("created_at", ""),
            "last_used": k.get("last_used"),
            "revoked": k.get("revoked", False),
            "requests_30d": k.get("requests_30d", 0),
        })
    total_requests = sum(k["requests_30d"] for k in items)
    return {"app_name": html.escape(app_name), "keys": items,
            "total": len(items), "active": active,
            "total_requests_30d": total_requests,
            "can_create": active < 10}


def create_app_key(*, app_id: str, name: str, scopes: list[str]) -> dict:
    key = f"osk_{secrets.token_hex(24)}"
    return {"key": key, "prefix": key[:8], "name": html.escape(name),
            "scopes": scopes, "app_id": app_id,
            "created_at": datetime.now(timezone.utc).isoformat()}
