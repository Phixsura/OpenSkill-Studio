"""Fleet DB Replication v9 — track database replication lag and health."""
from __future__ import annotations
def fleet_db_replication_v9(replicas: list[dict]) -> dict:
    synced = [r for r in replicas if r.get("lag_ms", 0) < 100]
    lagging = [r for r in replicas if r.get("lag_ms", 0) >= 100]
    max_lag = max((r.get("lag_ms", 0) for r in replicas), default=0)
    return {"replicas": len(replicas), "synced": len(synced), "lagging": len(lagging),
            "max_lag_ms": max_lag, "healthy": len(lagging) == 0}
