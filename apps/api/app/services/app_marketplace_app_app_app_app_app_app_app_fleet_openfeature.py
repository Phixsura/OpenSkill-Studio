"""Fleet OpenFeature — track feature flag provider adoption."""
from __future__ import annotations
def fleet_openfeature(providers: list[dict]) -> dict:
    active = [p for p in providers if p.get("active", True)]
    evaluations = sum(p.get("evaluations_24h", 0) for p in providers)
    return {"total": len(providers), "active": len(active), "evaluations_24h": evaluations,
            "standard_adopted": len(active) > 0}
