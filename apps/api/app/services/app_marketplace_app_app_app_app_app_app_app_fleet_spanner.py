"""Fleet Cloud Spanner — track globally distributed database."""
from __future__ import annotations
def fleet_spanner_status(instances: list[dict]) -> dict:
    ready = [i for i in instances if i.get("state") == "READY"]
    total_nodes = sum(i.get("nodes", 0) for i in instances)
    cpu_pct = round(sum(i.get("cpu_pct", 0) for i in instances) / max(len(instances), 1), 1)
    return {"instances": len(instances), "ready": len(ready), "nodes": total_nodes,
            "cpu_pct": cpu_pct, "all_ready": len(ready) == len(instances)}
