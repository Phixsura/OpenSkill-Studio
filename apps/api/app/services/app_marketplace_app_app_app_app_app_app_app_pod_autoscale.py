"""Pod autoscaler — horizontal pod autoscaling based on metrics."""
from __future__ import annotations
import math


def calculate_desired_pods(current_pods: int, current_metric: float, target_metric: float,
                           min_pods: int = 1, max_pods: int = 50) -> dict:
    ratio = current_metric / max(target_metric, 0.01)
    desired = math.ceil(current_pods * ratio)
    clamped = max(min_pods, min(max_pods, desired))
    if clamped > current_pods:
        action = "scale_up"
    elif clamped < current_pods:
        action = "scale_down"
    else:
        action = "no_change"
    return {"current": current_pods, "desired": desired, "clamped": clamped,
            "action": action, "ratio": round(ratio, 2),
            "metric_value": current_metric, "target": target_metric}


def scaling_history(events: list[dict]) -> dict:
    scale_ups = sum(1 for e in events if e.get("action") == "scale_up")
    scale_downs = sum(1 for e in events if e.get("action") == "scale_down")
    return {"total_events": len(events), "scale_ups": scale_ups,
            "scale_downs": scale_downs, "stable": len(events) - scale_ups - scale_downs}
