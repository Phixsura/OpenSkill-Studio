"""Fleet Database Health v9 — track database cluster health and metrics."""
from __future__ import annotations
def fleet_database_health_v9(databases: list[dict]) -> dict:
    healthy_db = [d for d in databases if d.get("healthy")]
    connections = sum(d.get("active_connections", 0) for d in databases)
    qps = sum(d.get("queries_per_sec", 0) for d in databases)
    replication_lag = max((d.get("replication_lag_ms", 0) for d in databases), default=0)
    return {"databases": len(databases), "healthy": len(healthy_db), "connections": connections,
            "qps": qps, "max_replication_lag_ms": replication_lag, "all_healthy": len(healthy_db) == len(databases)}
