"""Fleet gateway plugins — track active gateway plugins."""
from __future__ import annotations
def fleet_gw_plugins(plugins: list[dict]) -> dict:
    active = [p for p in plugins if p.get("enabled", False)]
    deprecated = [p for p in plugins if p.get("deprecated", False)]
    return {"total": len(plugins), "active": len(active), "deprecated": len(deprecated),
            "healthy": len(deprecated) == 0}
