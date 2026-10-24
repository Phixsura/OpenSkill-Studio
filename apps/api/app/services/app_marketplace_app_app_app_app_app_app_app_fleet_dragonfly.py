"""Fleet Dragonfly — track modern in-memory datastore."""
from __future__ import annotations
def fleet_dragonfly_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    memory_gb = sum(i.get("memory_gb", 0) for i in instances)
    throughput = sum(i.get("ops_per_sec", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "memory_gb": memory_gb,
            "ops_per_sec": throughput, "high_perf": throughput > 1000000}
