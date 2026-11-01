"""Fleet ScyllaDB — track high-performance NoSQL database."""
from __future__ import annotations
def fleet_scylladb_status(nodes: list[dict]) -> dict:
    up = [n for n in nodes if n.get("status") == "UN"]
    total_ops = sum(n.get("ops_per_sec", 0) for n in nodes)
    p99_lat = round(sum(n.get("p99_ms", 0) for n in nodes) / max(len(nodes), 1), 1)
    return {"nodes": len(nodes), "up": len(up), "ops_per_sec": total_ops,
            "p99_ms": p99_lat, "healthy": len(up) == len(nodes)}
