"""Fleet PocketBase — track embedded BaaS instances."""
from __future__ import annotations
def fleet_pocketbase_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    collections = sum(i.get("collections", 0) for i in instances)
    records = sum(i.get("records", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "collections": collections,
            "records": records, "all_running": len(running) == len(instances)}
