"""Fleet ClickHouse — track OLAP analytics database health."""
from __future__ import annotations
def fleet_clickhouse_status(shards: list[dict]) -> dict:
    healthy = [s for s in shards if s.get("healthy", True)]
    total_rows = sum(s.get("total_rows", 0) for s in shards)
    queries_per_sec = sum(s.get("qps", 0) for s in shards)
    return {"shards": len(shards), "healthy": len(healthy), "total_rows": total_rows,
            "qps": queries_per_sec, "all_healthy": len(healthy) == len(shards)}
