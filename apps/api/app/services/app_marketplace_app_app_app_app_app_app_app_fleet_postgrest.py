"""Fleet PostgREST — track auto-generated REST API health."""
from __future__ import annotations
def fleet_postgrest_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    total_rps = sum(i.get("rps", 0) for i in instances)
    schemas = sum(i.get("schemas", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "rps": total_rps,
            "schemas": schemas, "all_running": len(running) == len(instances)}
