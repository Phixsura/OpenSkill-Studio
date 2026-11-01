"""Fleet Secret Rotation v9 — track secret lifecycle management."""
from __future__ import annotations
def fleet_secret_rotation_v9(secrets: list[dict]) -> dict:
    rotated = [s for s in secrets if s.get("rotated")]
    expired = [s for s in secrets if s.get("expired")]
    return {"total": len(secrets), "rotated": len(rotated), "expired": len(expired),
            "rotation_rate": round(len(rotated) / len(secrets) * 100, 1) if secrets else 0,
            "healthy": len(expired) == 0}
