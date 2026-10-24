"""Fleet Durable Objects — track stateful edge computing."""
from __future__ import annotations
def fleet_durable_objects(namespaces: list[dict]) -> dict:
    active = sum(n.get("active_objects", 0) for n in namespaces)
    storage_mb = sum(n.get("storage_mb", 0) for n in namespaces)
    requests = sum(n.get("requests_24h", 0) for n in namespaces)
    return {"namespaces": len(namespaces), "active_objects": active, "storage_mb": storage_mb,
            "requests_24h": requests, "in_use": active > 0}
