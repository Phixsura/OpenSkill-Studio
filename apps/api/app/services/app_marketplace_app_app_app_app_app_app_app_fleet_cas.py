"""Fleet cluster autoscaler — track CAS decisions."""
from __future__ import annotations
def fleet_cluster_autoscaler(events: list[dict]) -> dict:
    scale_ups = [e for e in events if e.get("action") == "scale_up"]
    scale_downs = [e for e in events if e.get("action") == "scale_down"]
    failed = [e for e in events if e.get("status") == "failed"]
    return {"total_events": len(events), "scale_ups": len(scale_ups),
            "scale_downs": len(scale_downs), "failed": len(failed), "healthy": len(failed) == 0}
