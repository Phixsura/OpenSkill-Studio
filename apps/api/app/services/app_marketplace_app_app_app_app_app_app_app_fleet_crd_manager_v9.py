"""Fleet CRD Manager v9 — track Custom Resource Definition lifecycle."""
from __future__ import annotations
def fleet_crd_manager_v9(crds: list[dict]) -> dict:
    established = [c for c in crds if c.get("status") == "established"]
    instances = sum(c.get("instances", 0) for c in crds)
    versions = sum(c.get("versions", 1) for c in crds)
    return {"crds": len(crds), "established": len(established), "total_instances": instances,
            "total_versions": versions, "healthy": len(established) == len(crds)}
