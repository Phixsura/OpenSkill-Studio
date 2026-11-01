"""Fleet Storage Tiering v9 — track hot/warm/cold data placement."""
from __future__ import annotations
def fleet_storage_tiering_v9(tiers: list[dict]) -> dict:
    hot = sum(t.get("size_gb", 0) for t in tiers if t.get("tier") == "hot")
    warm = sum(t.get("size_gb", 0) for t in tiers if t.get("tier") == "warm")
    cold = sum(t.get("size_gb", 0) for t in tiers if t.get("tier") == "cold")
    total = hot + warm + cold
    return {"tiers": len(tiers), "hot_gb": hot, "warm_gb": warm, "cold_gb": cold,
            "total_gb": total, "healthy": total > 0}
