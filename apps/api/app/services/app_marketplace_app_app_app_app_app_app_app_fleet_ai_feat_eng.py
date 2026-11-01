"""Fleet AI Feature Engineering — track automated feature creation."""
from __future__ import annotations
def fleet_ai_feature_engineering(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    features_created = sum(e.get("features", 0) for e in engines)
    transforms = sum(e.get("transforms", 0) for e in engines)
    impact_pct = round(sum(e.get("impact_pct", 0) for e in engines) / max(len(engines), 1), 1)
    return {"engines": len(engines), "active": len(active), "features": features_created,
            "transforms": transforms, "impact_pct": impact_pct, "impactful": impact_pct > 10}
