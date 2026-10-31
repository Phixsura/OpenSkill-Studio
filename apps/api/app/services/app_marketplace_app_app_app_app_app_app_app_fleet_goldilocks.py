"""Fleet Goldilocks — track right-sizing recommendations."""
from __future__ import annotations
def fleet_goldilocks(namespaces: list[dict]) -> dict:
    enabled = [n for n in namespaces if n.get("goldilocks_enabled", False)]
    recommendations = sum(n.get("recommendations", 0) for n in enabled)
    return {"total": len(namespaces), "enabled": len(enabled), "recommendations": recommendations,
            "adopted": len(enabled) == len(namespaces)}
