"""Platform autoscaler — scale services based on metrics."""
from __future__ import annotations


def calculate_replicas(current: int, cpu_pct: float, target_cpu: float = 70,
                       min_replicas: int = 1, max_replicas: int = 20) -> dict:
    desired = max(1, round(current * cpu_pct / target_cpu))
    clamped = max(min_replicas, min(max_replicas, desired))
    action = "scale_up" if clamped > current else ("scale_down" if clamped < current else "no_change")
    return {"current": current, "desired": desired, "clamped": clamped,
            "action": action, "cpu_pct": cpu_pct, "target_cpu": target_cpu}


def cooldown_check(last_scale_at: float, now: float, cooldown_seconds: int = 300) -> dict:
    elapsed = now - last_scale_at
    can_scale = elapsed >= cooldown_seconds
    return {"can_scale": can_scale, "elapsed": round(elapsed),
            "remaining": max(0, round(cooldown_seconds - elapsed))}


def fleet_status(services: list[dict]) -> dict:
    total_replicas = sum(s.get("replicas", 1) for s in services)
    scaling = [s for s in services if s.get("action") != "no_change"]
    return {"services": len(services), "total_replicas": total_replicas,
            "currently_scaling": len(scaling),
            "avg_cpu": round(sum(s.get("cpu_pct", 0) for s in services) / max(len(services), 1), 1)}
