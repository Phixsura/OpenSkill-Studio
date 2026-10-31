"""Fleet AI Memory Manager — track AI GPU and system memory optimization."""
from __future__ import annotations
def fleet_ai_memory_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    total_gb = round(sum(m.get("total_gb", 0) for m in managers), 1)
    used_gb = round(sum(m.get("used_gb", 0) for m in managers), 1)
    utilization = round(used_gb / max(total_gb, 1) * 100, 1)
    oom_events = sum(m.get("oom_24h", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "total_gb": total_gb,
            "used_gb": used_gb, "utilization": utilization, "oom_24h": oom_events, "stable": oom_events == 0}
