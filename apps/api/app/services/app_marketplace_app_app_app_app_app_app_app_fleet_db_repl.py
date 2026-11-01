"""Fleet DB replication lag — track replication lag across replicas."""
from __future__ import annotations
def fleet_db_repl_lag(replicas: list[dict]) -> dict:
    max_lag = max((r.get("lag_ms", 0) for r in replicas), default=0)
    avg_lag = round(sum(r.get("lag_ms", 0) for r in replicas) / max(len(replicas), 1), 1)
    behind = [r for r in replicas if r.get("lag_ms", 0) > 1000]
    return {"replicas": len(replicas), "max_lag_ms": max_lag, "avg_lag_ms": avg_lag,
            "behind": len(behind), "healthy": max_lag < 1000}
