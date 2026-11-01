"""Fleet AI Idempotency Key — track request deduplication via idempotency."""
from __future__ import annotations
def fleet_ai_idempotency_key(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    keys_active = sum(m.get("keys", 0) for m in managers)
    duplicates_prevented = sum(m.get("prevented", 0) for m in managers)
    ttl_s = max((m.get("ttl_s", 0) for m in managers), default=0)
    return {"managers": len(managers), "active": len(active), "keys": keys_active,
            "prevented": duplicates_prevented, "ttl_s": ttl_s, "protecting": duplicates_prevented > 0}
