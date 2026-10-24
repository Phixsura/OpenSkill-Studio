"""Fleet CRD status — track custom resource definition health."""
from __future__ import annotations
def fleet_crd_status(crds: list[dict]) -> dict:
    healthy = [c for c in crds if c.get("condition") == "Established"]
    stale = [c for c in crds if c.get("age_days", 0) > 365]
    return {"total": len(crds), "healthy": len(healthy), "stale": len(stale),
            "all_established": len(healthy) == len(crds)}
