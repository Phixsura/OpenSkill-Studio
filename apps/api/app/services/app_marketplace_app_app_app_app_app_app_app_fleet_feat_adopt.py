"""Fleet feature adoption — track feature rollout adoption rates."""
from __future__ import annotations
def fleet_feature_adoption(features: list[dict]) -> dict:
    adopted = [f for f in features if f.get("adoption_pct", 0) >= 50]
    avg_adoption = round(sum(f.get("adoption_pct", 0) for f in features) / max(len(features), 1), 1)
    return {"total": len(features), "widely_adopted": len(adopted),
            "avg_adoption_pct": avg_adoption, "good": avg_adoption >= 60}
