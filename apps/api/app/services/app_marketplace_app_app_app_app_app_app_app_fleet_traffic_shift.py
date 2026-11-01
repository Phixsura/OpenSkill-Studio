"""Fleet traffic shift — track gradual traffic migration."""
from __future__ import annotations
def fleet_traffic_shift(targets: list[dict]) -> dict:
    total_weight = sum(t.get("weight", 0) for t in targets)
    primary = max(targets, key=lambda t: t.get("weight", 0)) if targets else None
    return {"targets": len(targets), "total_weight": total_weight,
            "primary": primary.get("name") if primary else None,
            "primary_pct": round(primary.get("weight", 0) / max(total_weight, 1) * 100, 1) if primary else 0}
