"""Fleet Feature Adoption v9 — track feature usage and adoption rates."""
from __future__ import annotations
def fleet_feature_adoption_v9(features: list[dict]) -> dict:
    launched = [f for f in features if f.get("launched")]
    adopted = [f for f in features if f.get("adoption_pct", 0) > 50]
    avg_adoption = sum(f.get("adoption_pct", 0) for f in features) / len(features) if features else 0
    return {"features": len(features), "launched": len(launched), "widely_adopted": len(adopted),
            "avg_adoption_pct": round(avg_adoption, 1), "healthy": avg_adoption > 50}
