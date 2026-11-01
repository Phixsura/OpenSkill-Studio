"""Fleet SurrealDB — track multi-model database health."""
from __future__ import annotations
def fleet_surrealdb_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    namespaces = sum(i.get("namespaces", 0) for i in instances)
    tables = sum(i.get("tables", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "namespaces": namespaces,
            "tables": tables, "all_running": len(running) == len(instances)}
