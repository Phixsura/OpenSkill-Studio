"""Fleet Model Registry — track ML model lifecycle."""
from __future__ import annotations
def fleet_model_registry(registries: list[dict]) -> dict:
    models = sum(r.get("models", 0) for r in registries)
    versions = sum(r.get("versions", 0) for r in registries)
    deployed = sum(r.get("deployed_versions", 0) for r in registries)
    return {"registries": len(registries), "models": models, "versions": versions,
            "deployed": deployed, "deployment_rate": round(deployed / max(versions, 1) * 100, 1)}
