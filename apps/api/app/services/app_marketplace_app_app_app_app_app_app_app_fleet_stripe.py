"""Fleet Stripe — track payment platform integration."""
from __future__ import annotations
def fleet_stripe_status(accounts: list[dict]) -> dict:
    active = [a for a in accounts if a.get("active", True)]
    total_volume = sum(a.get("volume_24h_usd", 0) for a in accounts)
    success_rate = round(sum(a.get("success_rate", 100) for a in accounts) / max(len(accounts), 1), 1)
    return {"accounts": len(accounts), "active": len(active), "volume_24h": round(total_volume, 2),
            "success_rate": success_rate, "healthy": success_rate >= 99}
