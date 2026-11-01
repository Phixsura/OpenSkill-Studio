"""Fleet connection draining — track graceful connection draining."""
from __future__ import annotations
def fleet_conn_draining(pods: list[dict]) -> dict:
    draining = [p for p in pods if p.get("draining", False)]
    avg_drain = round(sum(p.get("drain_time_sec", 0) for p in draining) / max(len(draining), 1), 1) if draining else 0
    return {"total": len(pods), "draining": len(draining), "avg_drain_sec": avg_drain,
            "all_drained": len(draining) == 0}
