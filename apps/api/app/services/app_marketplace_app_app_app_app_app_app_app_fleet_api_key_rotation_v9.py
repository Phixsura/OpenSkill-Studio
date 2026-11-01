"""Fleet API Key Rotation v9 — track API key rotation automation."""
from __future__ import annotations
def fleet_api_key_rotation_v9(keys: list[dict]) -> dict:
    rotated = [k for k in keys if k.get("rotated_recently")]
    expired = [k for k in keys if k.get("expired")]
    avg_age = sum(k.get("age_days", 0) for k in keys) / len(keys) if keys else 0
    return {"keys": len(keys), "rotated_recently": len(rotated), "expired": len(expired),
            "avg_age_days": round(avg_age, 1), "healthy": len(expired) == 0}
