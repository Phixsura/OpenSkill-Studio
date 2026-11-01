"""Fleet API key management — track key lifecycle."""
from __future__ import annotations
def fleet_apikey_mgmt(keys: list[dict]) -> dict:
    active = [k for k in keys if k.get("status") == "active"]
    expired = [k for k in keys if k.get("status") == "expired"]
    expiring = [k for k in keys if k.get("days_until_expiry", 999) < 30 and k.get("status") == "active"]
    return {"total": len(keys), "active": len(active), "expired": len(expired),
            "expiring_soon": len(expiring), "needs_rotation": len(expiring) > 0}
