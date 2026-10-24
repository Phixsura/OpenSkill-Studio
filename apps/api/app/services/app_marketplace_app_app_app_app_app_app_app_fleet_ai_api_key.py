"""Fleet AI API Key Manager — track API key lifecycle management."""
from __future__ import annotations
def fleet_ai_api_key_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    keys_active = sum(m.get("keys_active", 0) for m in managers)
    keys_revoked_24h = sum(m.get("revoked_24h", 0) for m in managers)
    requests_24h = sum(m.get("requests_24h", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "keys_active": keys_active,
            "revoked_24h": keys_revoked_24h, "requests_24h": requests_24h, "managed": keys_active > 0}
