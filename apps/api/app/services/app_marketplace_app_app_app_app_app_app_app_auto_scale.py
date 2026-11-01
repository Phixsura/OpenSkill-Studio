"""Automated scaling policy — define and evaluate scaling policies."""
from __future__ import annotations
import math


def create_scaling_policy(name: str, metric: str, target_value: float,
                           min_replicas: int = 1, max_replicas: int = 10,
                           scale_up_cooldown: int = 60, scale_down_cooldown: int = 300) -> dict:
    return {"name": name, "metric": metric, "target_value": target_value,
            "min_replicas": min_replicas, "max_replicas": max_replicas,
            "scale_up_cooldown": scale_up_cooldown, "scale_down_cooldown": scale_down_cooldown}


def evaluate_scaling_decision(policy: dict, current_replicas: int,
                                current_value: float) -> dict:
    ratio = current_value / max(policy["target_value"], 0.01)
    desired = math.ceil(current_replicas * ratio)
    desired = max(policy["min_replicas"], min(policy["max_replicas"], desired))
    if desired > current_replicas:
        return {"action": "scale_up", "current": current_replicas, "desired": desired,
                "change": desired - current_replicas, "cooldown_sec": policy["scale_up_cooldown"]}
    elif desired < current_replicas:
        return {"action": "scale_down", "current": current_replicas, "desired": desired,
                "change": current_replicas - desired, "cooldown_sec": policy["scale_down_cooldown"]}
    return {"action": "none", "current": current_replicas, "desired": desired, "change": 0}
