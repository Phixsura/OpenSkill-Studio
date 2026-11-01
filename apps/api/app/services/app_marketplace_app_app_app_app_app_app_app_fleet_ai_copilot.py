"""Fleet AI Copilot — track AI assistant deployments."""
from __future__ import annotations
def fleet_ai_copilot(copilots: list[dict]) -> dict:
    active = [c for c in copilots if c.get("active", True)]
    interactions_24h = sum(c.get("interactions_24h", 0) for c in copilots)
    satisfaction = round(sum(c.get("satisfaction_pct", 0) for c in copilots) / max(len(copilots), 1), 1)
    return {"copilots": len(copilots), "active": len(active), "interactions_24h": interactions_24h,
            "satisfaction": satisfaction, "high_quality": satisfaction >= 85}
