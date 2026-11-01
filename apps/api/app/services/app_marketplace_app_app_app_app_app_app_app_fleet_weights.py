"""Fleet Weights — track model weight management."""
from __future__ import annotations
def fleet_weights_status(registries: list[dict]) -> dict:
    active = [r for r in registries if r.get("active", True)]
    models = sum(r.get("models", 0) for r in registries)
    versions = sum(r.get("versions", 0) for r in registries)
    storage_tb = sum(r.get("storage_tb", 0) for r in registries)
    return {"registries": len(registries), "active": len(active), "models": models,
            "versions": versions, "storage_tb": round(storage_tb, 1)}
