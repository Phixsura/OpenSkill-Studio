"""Fleet Twilio — track communications platform."""
from __future__ import annotations
def fleet_twilio_status(accounts: list[dict]) -> dict:
    active = [a for a in accounts if a.get("active", True)]
    messages_24h = sum(a.get("messages_24h", 0) for a in accounts)
    calls_24h = sum(a.get("calls_24h", 0) for a in accounts)
    return {"accounts": len(accounts), "active": len(active), "messages_24h": messages_24h,
            "calls_24h": calls_24h, "all_active": len(active) == len(accounts)}
