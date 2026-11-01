"""Fleet AI Spot Instance — track preemptible GPU instance management."""
from __future__ import annotations
def fleet_ai_spot_instance(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    instances = sum(m.get("instances", 0) for m in managers)
    savings_pct = round(sum(m.get("savings_pct", 0) for m in managers) / max(len(managers), 1), 1)
    interruptions_24h = sum(m.get("interruptions", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "instances": instances,
            "savings_pct": savings_pct, "interruptions": interruptions_24h, "cost_effective": savings_pct > 50}
