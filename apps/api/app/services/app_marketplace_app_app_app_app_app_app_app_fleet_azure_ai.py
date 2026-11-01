"""Fleet Azure AI — track Azure cognitive services."""
from __future__ import annotations
def fleet_azure_ai(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    api_calls_24h = sum(s.get("calls_24h", 0) for s in services)
    models = sum(s.get("deployed_models", 0) for s in services)
    return {"services": len(services), "active": len(active), "calls_24h": api_calls_24h,
            "models": models, "all_active": len(active) == len(services)}
