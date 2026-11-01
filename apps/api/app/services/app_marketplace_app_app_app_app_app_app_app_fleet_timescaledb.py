"""Fleet TimescaleDB — track time-series database health."""
from __future__ import annotations
def fleet_timescaledb_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    chunks = sum(i.get("chunks", 0) for i in instances)
    compression_ratio = round(sum(i.get("compression_ratio", 1) for i in instances) / max(len(instances), 1), 1)
    return {"instances": len(instances), "healthy": len(healthy), "chunks": chunks,
            "compression_ratio": compression_ratio, "all_healthy": len(healthy) == len(instances)}
