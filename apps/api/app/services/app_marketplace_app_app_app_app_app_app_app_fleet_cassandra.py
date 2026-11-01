"""Fleet Cassandra — track wide-column store health."""
from __future__ import annotations
def fleet_cassandra_status(nodes: list[dict]) -> dict:
    up = [n for n in nodes if n.get("status") == "UN"]
    down = [n for n in nodes if n.get("status") == "DN"]
    total_load_gb = sum(n.get("load_gb", 0) for n in nodes)
    return {"nodes": len(nodes), "up": len(up), "down": len(down),
            "total_load_gb": round(total_load_gb, 1), "healthy": len(down) == 0}
