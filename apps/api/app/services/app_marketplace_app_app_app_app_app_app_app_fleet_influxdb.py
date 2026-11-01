"""Fleet InfluxDB — track time-series database health."""
from __future__ import annotations
def fleet_influxdb_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    series = sum(i.get("series", 0) for i in instances)
    writes_per_sec = sum(i.get("writes_per_sec", 0) for i in instances)
    return {"instances": len(instances), "healthy": len(healthy), "series": series,
            "writes_per_sec": writes_per_sec, "all_healthy": len(healthy) == len(instances)}
