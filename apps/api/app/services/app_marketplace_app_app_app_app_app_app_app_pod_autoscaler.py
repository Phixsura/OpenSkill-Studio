"""Pod autoscaler — compute target replicas based on CPU/memory/custom metrics."""
from __future__ import annotations
import math


def compute_replicas(*, current_replicas: int, current_cpu_pct: float,
                      target_cpu_pct: float = 70, min_replicas: int = 2,
                      max_replicas: int = 20, scale_up_factor: float = 1.5,
                      cooldown_remaining_sec: int = 0) -> dict:
    if cooldown_remaining_sec > 0:
        return {"target_replicas": current_replicas, "action": "cooldown",
                "cooldown_remaining": cooldown_remaining_sec}
    ratio = current_cpu_pct / max(target_cpu_pct, 1)
    desired = math.ceil(current_replicas * ratio)
    # Limit scale-up speed
    max_up = math.ceil(current_replicas * scale_up_factor)
    desired = min(desired, max_up)
    # Clamp
    target = max(min_replicas, min(desired, max_replicas))
    if target > current_replicas:
        action = "scale_up"
    elif target < current_replicas:
        action = "scale_down"
    else:
        action = "none"
    return {
        "current_replicas": current_replicas, "target_replicas": target,
        "action": action, "current_cpu_pct": current_cpu_pct,
        "target_cpu_pct": target_cpu_pct, "ratio": round(ratio, 2),
        "min": min_replicas, "max": max_replicas,
    }
