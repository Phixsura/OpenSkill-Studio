"""Resource scaler — autoscale resources based on metrics."""
from __future__ import annotations


def create_scaling_policy(name: str, min_replicas: int = 1, max_replicas: int = 10,
                           target_cpu: float = 70.0, cooldown_sec: int = 300) -> dict:
    return {"name": name, "min_replicas": min_replicas, "max_replicas": max_replicas,
            "target_cpu": target_cpu, "cooldown_sec": cooldown_sec}


def evaluate_scaling(policy: dict, current_replicas: int, current_cpu: float) -> dict:
    desired = round(current_replicas * (current_cpu / policy["target_cpu"]))
    desired = max(policy["min_replicas"], min(policy["max_replicas"], desired))
    action = "scale_up" if desired > current_replicas else "scale_down" if desired < current_replicas else "none"
    return {"current": current_replicas, "desired": desired, "action": action,
            "current_cpu": current_cpu, "target_cpu": policy["target_cpu"],
            "change": desired - current_replicas}


def scaling_history(events: list[dict]) -> dict:
    scale_ups = sum(1 for e in events if e.get("action") == "scale_up")
    scale_downs = sum(1 for e in events if e.get("action") == "scale_down")
    return {"total_events": len(events), "scale_ups": scale_ups,
            "scale_downs": scale_downs, "stable": scale_ups + scale_downs == 0}
