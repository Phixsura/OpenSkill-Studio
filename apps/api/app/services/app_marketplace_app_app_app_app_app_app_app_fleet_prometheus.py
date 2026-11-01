"""Fleet Prometheus — track Prometheus health and cardinality."""
from __future__ import annotations
def fleet_prometheus_health(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    total_series = sum(i.get("active_series", 0) for i in instances)
    storage_gb = sum(i.get("storage_gb", 0) for i in instances)
    return {"instances": len(instances), "healthy": len(healthy), "total_series": total_series,
            "storage_gb": storage_gb, "all_healthy": len(healthy) == len(instances)}
