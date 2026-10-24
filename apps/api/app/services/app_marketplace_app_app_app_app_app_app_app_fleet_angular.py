"""Fleet Angular — track enterprise SPA framework."""
from __future__ import annotations
def fleet_angular_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    components = sum(a.get("components", 0) for a in apps)
    modules = sum(a.get("modules", 0) for a in apps)
    bundle_kb = round(sum(a.get("bundle_kb", 0) for a in apps) / max(len(apps), 1), 1)
    return {"apps": len(apps), "deployed": len(deployed), "components": components,
            "modules": modules, "avg_bundle_kb": bundle_kb}
