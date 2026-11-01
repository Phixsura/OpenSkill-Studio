"""Fleet Token Rotation v9 — track automated token/key rotation."""
from __future__ import annotations
def fleet_token_rotation_v9(tokens: list[dict]) -> dict:
    rotated = [t for t in tokens if t.get("rotated")]
    expired = [t for t in tokens if t.get("expired")]
    avg_age = sum(t.get("age_days", 0) for t in tokens) / len(tokens) if tokens else 0
    return {"total": len(tokens), "rotated": len(rotated), "expired": len(expired),
            "avg_age_days": round(avg_age, 1), "healthy": len(expired) == 0}
