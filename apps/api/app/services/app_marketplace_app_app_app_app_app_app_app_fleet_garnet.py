"""Fleet Garnet — track Microsoft Garnet cache store."""
from __future__ import annotations
def fleet_garnet_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    total_ops = sum(i.get("ops_per_sec", 0) for i in instances)
    p99_us = round(sum(i.get("p99_us", 0) for i in instances) / max(len(instances), 1), 1)
    return {"instances": len(instances), "healthy": len(healthy), "ops_per_sec": total_ops,
            "p99_us": p99_us, "ultra_fast": p99_us < 100}
