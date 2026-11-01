"""Fleet Pod Autoscaler v9 — track VPA and HPA recommendations."""
from __future__ import annotations
def fleet_pod_autoscaler_v9(autoscalers: list[dict]) -> dict:
    hpa = [a for a in autoscalers if a.get("type") == "HPA"]
    vpa = [a for a in autoscalers if a.get("type") == "VPA"]
    scale_events = sum(a.get("events_today", 0) for a in autoscalers)
    return {"autoscalers": len(autoscalers), "hpa": len(hpa), "vpa": len(vpa),
            "scale_events_today": scale_events, "healthy": True}
