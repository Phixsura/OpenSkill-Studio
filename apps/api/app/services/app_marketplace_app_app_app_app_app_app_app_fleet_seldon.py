"""Fleet Seldon — track ML deployment platform."""
from __future__ import annotations
def fleet_seldon_status(deployments: list[dict]) -> dict:
    available = [d for d in deployments if d.get("available", True)]
    predictors = sum(d.get("predictors", 0) for d in deployments)
    requests_24h = sum(d.get("requests_24h", 0) for d in deployments)
    return {"deployments": len(deployments), "available": len(available), "predictors": predictors,
            "requests_24h": requests_24h, "all_available": len(available) == len(deployments)}
