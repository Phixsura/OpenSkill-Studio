"""Fleet YugabyteDB — track distributed PostgreSQL."""
from __future__ import annotations
def fleet_yugabyte_status(clusters: list[dict]) -> dict:
    running = [c for c in clusters if c.get("status") == "RUNNING"]
    tablets = sum(c.get("tablets", 0) for c in clusters)
    tserver_nodes = sum(c.get("tservers", 0) for c in clusters)
    return {"clusters": len(clusters), "running": len(running), "tablets": tablets,
            "tservers": tserver_nodes, "all_running": len(running) == len(clusters)}
