"""Fleet Service Account v9 — track service account permissions and usage."""
from __future__ import annotations
def fleet_service_account_v9(accounts: list[dict]) -> dict:
    active = [a for a in accounts if a.get("active")]
    over_privileged = [a for a in accounts if a.get("over_privileged")]
    last_used = [a for a in accounts if a.get("used_this_week")]
    return {"total": len(accounts), "active": len(active), "over_privileged": len(over_privileged),
            "used_this_week": len(last_used), "healthy": len(over_privileged) == 0}
