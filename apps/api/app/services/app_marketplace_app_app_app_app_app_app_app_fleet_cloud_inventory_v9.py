"""Fleet Cloud Inventory v9 — track all cloud resources inventory."""
from __future__ import annotations
def fleet_cloud_inventory_v9(resources: list[dict]) -> dict:
    types = len({r.get("type") for r in resources if r.get("type")})
    regions = len({r.get("region") for r in resources if r.get("region")})
    tagged = [r for r in resources if r.get("tagged")]
    return {"resources": len(resources), "resource_types": types, "regions": regions,
            "tagged": len(tagged), "healthy": len(tagged) == len(resources)}
