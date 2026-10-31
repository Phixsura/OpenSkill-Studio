"""Fleet Dapr — track Dapr sidecar runtime health."""
from __future__ import annotations
def fleet_dapr_status(apps: list[dict]) -> dict:
    healthy = [a for a in apps if a.get("sidecar_healthy", True)]
    components = sum(a.get("components", 0) for a in apps)
    return {"total": len(apps), "healthy": len(healthy), "components": components,
            "all_healthy": len(healthy) == len(apps)}
