"""Fleet Directus — track data platform health."""
from __future__ import annotations
def fleet_directus_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    collections = sum(i.get("collections", 0) for i in instances)
    items = sum(i.get("items", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "collections": collections,
            "items": items, "all_running": len(running) == len(instances)}
