"""Fleet AI Platform Inventory — track AI infrastructure asset inventory."""
from __future__ import annotations
def fleet_ai_platform_inventory(inventories: list[dict]) -> dict:
    active = [i for i in inventories if i.get("active", True)]
    assets = sum(i.get("assets", 0) for i in inventories)
    gpus = sum(i.get("gpus", 0) for i in inventories)
    storage_pb = round(sum(i.get("storage_pb", 0) for i in inventories), 1)
    return {"inventories": len(inventories), "active": len(active), "assets": assets,
            "gpus": gpus, "storage_pb": storage_pb, "complete": assets > 0}
