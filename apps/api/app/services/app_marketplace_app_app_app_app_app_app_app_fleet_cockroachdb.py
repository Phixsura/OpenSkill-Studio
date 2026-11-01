"""Fleet CockroachDB — track distributed SQL database health."""
from __future__ import annotations
def fleet_cockroachdb_status(nodes: list[dict]) -> dict:
    live = [n for n in nodes if n.get("live", True)]
    ranges = sum(n.get("ranges", 0) for n in nodes)
    under_replicated = sum(n.get("under_replicated", 0) for n in nodes)
    return {"nodes": len(nodes), "live": len(live), "ranges": ranges,
            "under_replicated": under_replicated, "healthy": under_replicated == 0}
