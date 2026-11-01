"""Fleet AI API Key v5 — track API key lifecycle at enterprise scale."""
from __future__ import annotations
def fleet_ai_apikey_v5(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    keys = sum(m.get("keys", 0) for m in managers)
    created_24h = sum(m.get("created", 0) for m in managers)
    revoked_24h = sum(m.get("revoked", 0) for m in managers)
    scoped = all(m.get("scoped", False) for m in managers)
    return {"managers": len(managers), "active": len(active), "keys": keys,
            "created_24h": created_24h, "revoked_24h": revoked_24h, "scoped": scoped, "governed": scoped}
