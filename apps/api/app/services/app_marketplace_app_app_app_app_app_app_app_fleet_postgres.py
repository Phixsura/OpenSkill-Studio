"""Fleet PostgreSQL — track database cluster health."""
from __future__ import annotations
def fleet_postgres_status(instances: list[dict]) -> dict:
    primary = [i for i in instances if i.get("role") == "primary"]
    replicas = [i for i in instances if i.get("role") == "replica"]
    max_lag = max((i.get("replication_lag_mb", 0) for i in replicas), default=0)
    total_conns = sum(i.get("active_connections", 0) for i in instances)
    return {"instances": len(instances), "primary": len(primary), "replicas": len(replicas),
            "max_replication_lag_mb": max_lag, "active_connections": total_conns,
            "healthy": max_lag < 100 and len(primary) == 1}
