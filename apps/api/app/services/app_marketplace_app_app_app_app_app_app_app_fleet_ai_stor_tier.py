"""Fleet AI Storage Tiering — track hot/warm/cold AI data tiering."""
from __future__ import annotations
def fleet_ai_storage_tiering(tiers: list[dict]) -> dict:
    active = [t for t in tiers if t.get("active", True)]
    hot_tb = round(sum(t.get("hot_tb", 0) for t in tiers), 1)
    warm_tb = round(sum(t.get("warm_tb", 0) for t in tiers), 1)
    cold_tb = round(sum(t.get("cold_tb", 0) for t in tiers), 1)
    cost_saved_pct = round(sum(t.get("saved_pct", 0) for t in tiers) / max(len(tiers), 1), 1)
    return {"tiers": len(tiers), "active": len(active), "hot_tb": hot_tb,
            "warm_tb": warm_tb, "cold_tb": cold_tb, "saved_pct": cost_saved_pct, "optimized": cost_saved_pct > 30}
