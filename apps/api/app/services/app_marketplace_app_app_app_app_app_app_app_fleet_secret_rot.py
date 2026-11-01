"""Fleet secret rotation — track secret/key rotation status."""
from __future__ import annotations
def fleet_secret_rotation(secrets: list[dict]) -> dict:
    stale = [s for s in secrets if s.get("age_days", 0) > 90]
    return {"total": len(secrets), "stale": len(stale),
            "fresh": len(secrets) - len(stale), "compliant": len(stale) == 0}
