"""Fleet Fauna — track serverless document database."""
from __future__ import annotations
def fleet_fauna_status(databases: list[dict]) -> dict:
    active = [d for d in databases if d.get("active", True)]
    collections = sum(d.get("collections", 0) for d in databases)
    read_ops = sum(d.get("read_ops_24h", 0) for d in databases)
    return {"databases": len(databases), "active": len(active), "collections": collections,
            "read_ops_24h": read_ops, "all_active": len(active) == len(databases)}
