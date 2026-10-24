"""Fleet etcd health — track etcd cluster health and size."""
from __future__ import annotations
def fleet_etcd_health(members: list[dict]) -> dict:
    healthy = [m for m in members if m.get("healthy", False)]
    total_keys = sum(m.get("key_count", 0) for m in members)
    db_size_mb = sum(m.get("db_size_mb", 0) for m in members)
    return {"members": len(members), "healthy": len(healthy), "total_keys": total_keys,
            "db_size_mb": db_size_mb, "quorum": len(healthy) > len(members) / 2}
