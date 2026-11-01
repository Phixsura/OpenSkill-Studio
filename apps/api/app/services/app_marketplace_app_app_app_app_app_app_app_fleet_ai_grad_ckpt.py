"""Fleet AI Gradient Checkpointing — track memory-efficient training."""
from __future__ import annotations
def fleet_ai_gradient_checkpoint(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    memory_saved_gb = round(sum(m.get("saved_gb", 0) for m in managers), 1)
    overhead_pct = round(sum(m.get("overhead_pct", 0) for m in managers) / max(len(managers), 1), 1)
    jobs_using = sum(m.get("jobs", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "saved_gb": memory_saved_gb,
            "overhead_pct": overhead_pct, "jobs": jobs_using, "efficient": overhead_pct < 30}
