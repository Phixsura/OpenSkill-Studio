"""Fleet AI Secret Rotation — track automated API key and secret rotation."""
from __future__ import annotations
def fleet_ai_secret_rotation(rotators: list[dict]) -> dict:
    active = [r for r in rotators if r.get("active", True)]
    secrets_managed = sum(r.get("secrets", 0) for r in rotators)
    rotations_24h = sum(r.get("rotations_24h", 0) for r in rotators)
    avg_age_days = round(sum(r.get("avg_age_days", 0) for r in rotators) / max(len(rotators), 1), 1)
    return {"rotators": len(rotators), "active": len(active), "secrets": secrets_managed,
            "rotations_24h": rotations_24h, "avg_age_days": avg_age_days, "fresh": avg_age_days < 30}
