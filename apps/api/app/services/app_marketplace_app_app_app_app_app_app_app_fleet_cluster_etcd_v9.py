"""Fleet Cluster etcd v9 — track etcd cluster health and performance."""
from __future__ import annotations
def fleet_cluster_etcd_v9(clusters: list[dict]) -> dict:
    healthy_e = [c for c in clusters if c.get("etcd_healthy")]
    db_size = sum(c.get("db_size_mb", 0) for c in clusters)
    leader_changes = sum(c.get("leader_changes", 0) for c in clusters)
    return {"clusters": len(clusters), "etcd_healthy": len(healthy_e), "total_db_size_mb": round(db_size, 1),
            "leader_changes": leader_changes, "healthy": len(healthy_e) == len(clusters)}
