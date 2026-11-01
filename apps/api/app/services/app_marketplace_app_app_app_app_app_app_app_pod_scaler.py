"""Pod autoscaler simulator — simulate Kubernetes HPA behavior."""
from __future__ import annotations
import math


def simulate_hpa(current_pods: int, current_cpu: float, target_cpu: float,
                  min_pods: int = 1, max_pods: int = 20) -> dict:
    desired = math.ceil(current_pods * (current_cpu / target_cpu))
    desired = max(min_pods, min(max_pods, desired))
    action = "scale_up" if desired > current_pods else "scale_down" if desired < current_pods else "stable"
    return {"current_pods": current_pods, "desired_pods": desired,
            "current_cpu": current_cpu, "target_cpu": target_cpu,
            "action": action, "change": desired - current_pods,
            "at_min": desired == min_pods, "at_max": desired == max_pods}


def forecast_pods(base_pods: int, traffic_multipliers: list[float],
                   target_cpu: float, cpu_per_rps: float) -> list[dict]:
    results = []
    for i, mult in enumerate(traffic_multipliers):
        cpu_needed = mult * cpu_per_rps * 100
        pods = max(1, math.ceil(cpu_needed / target_cpu))
        results.append({"period": i, "multiplier": mult,
                         "estimated_pods": pods, "cpu_pct": round(cpu_needed / pods, 1)})
    return results
