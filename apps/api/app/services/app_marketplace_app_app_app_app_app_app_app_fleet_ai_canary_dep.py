"""Fleet AI Canary Deploy — track progressive AI model rollouts."""
from __future__ import annotations
def fleet_ai_canary_deploy(deploys: list[dict]) -> dict:
    active = [d for d in deploys if d.get("active", True)]
    canary_pct = round(sum(d.get("canary_pct", 0) for d in deploys) / max(len(deploys), 1), 1)
    rollbacks = sum(d.get("rollbacks", 0) for d in deploys)
    promotions = sum(d.get("promotions", 0) for d in deploys)
    return {"deploys": len(deploys), "active": len(active), "canary_pct": canary_pct,
            "rollbacks": rollbacks, "promotions": promotions, "safe": rollbacks == 0}
