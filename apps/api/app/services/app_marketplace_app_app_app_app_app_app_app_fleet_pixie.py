"""Fleet Pixie — track eBPF-based auto-telemetry."""
from __future__ import annotations
def fleet_pixie_status(clusters: list[dict]) -> dict:
    connected = [c for c in clusters if c.get("connected", True)]
    total_pods = sum(c.get("monitored_pods", 0) for c in connected)
    data_gb = sum(c.get("data_retained_gb", 0) for c in clusters)
    return {"clusters": len(clusters), "connected": len(connected), "monitored_pods": total_pods,
            "data_retained_gb": round(data_gb, 1), "all_connected": len(connected) == len(clusters)}
