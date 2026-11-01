"""Fleet Cross-Region v9 — track multi-region replication and failover."""
from __future__ import annotations
def fleet_cross_region_v9(regions: list[dict]) -> dict:
    primary = [r for r in regions if r.get("role") == "primary"]
    replica = [r for r in regions if r.get("role") == "replica"]
    lag_ms = sum(r.get("replication_lag_ms", 0) for r in replica)
    return {"regions": len(regions), "primary": len(primary), "replicas": len(replica),
            "total_lag_ms": lag_ms, "healthy": lag_ms < 1000}
