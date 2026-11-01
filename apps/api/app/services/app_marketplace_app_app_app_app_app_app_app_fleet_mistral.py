"""Fleet Mistral — track Mistral AI integration."""
from __future__ import annotations
def fleet_mistral_status(deployments: list[dict]) -> dict:
    active = [d for d in deployments if d.get("active", True)]
    completions_24h = sum(d.get("completions_24h", 0) for d in deployments)
    tokens_24h = sum(d.get("tokens_24h", 0) for d in deployments)
    return {"deployments": len(deployments), "active": len(active), "completions_24h": completions_24h,
            "tokens_24h": tokens_24h, "all_active": len(active) == len(deployments)}
