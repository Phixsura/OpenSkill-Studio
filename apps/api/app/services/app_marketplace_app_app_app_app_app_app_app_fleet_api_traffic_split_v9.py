"""Fleet API Traffic Split v9 — track weighted traffic splitting."""
from __future__ import annotations
def fleet_api_traffic_split_v9(splits: list[dict]) -> dict:
    active = [s for s in splits if s.get("active")]
    canary_pct = sum(s.get("canary_pct", 0) for s in splits) / len(splits) if splits else 0
    total_rps = sum(s.get("rps", 0) for s in splits)
    return {"splits": len(splits), "active": len(active), "avg_canary_pct": round(canary_pct, 1),
            "total_rps": total_rps, "healthy": True}
