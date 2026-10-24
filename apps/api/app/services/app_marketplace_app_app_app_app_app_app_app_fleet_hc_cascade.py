"""Fleet health check cascade — track cascading health impacts."""
from __future__ import annotations
def fleet_hc_cascade(services: list[dict]) -> dict:
    unhealthy = [s for s in services if not s.get("healthy", True)]
    impacted = [s for s in services if s.get("impacted_by_dependency", False)]
    cascade_depth = max((s.get("cascade_depth", 0) for s in impacted), default=0)
    return {"total": len(services), "unhealthy": len(unhealthy), "impacted": len(impacted),
            "max_cascade_depth": cascade_depth, "cascading": len(impacted) > len(unhealthy)}
