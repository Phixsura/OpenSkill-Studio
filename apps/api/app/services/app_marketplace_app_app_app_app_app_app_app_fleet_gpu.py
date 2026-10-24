"""Fleet GPU utilization — track GPU usage for ML workloads."""
from __future__ import annotations
def fleet_gpu_utilization(gpus: list[dict]) -> dict:
    total = len(gpus)
    active = [g for g in gpus if g.get("util_pct", 0) > 10]
    avg_util = round(sum(g.get("util_pct", 0) for g in gpus) / max(total, 1), 1)
    return {"total": total, "active": len(active), "idle": total - len(active),
            "avg_util_pct": avg_util, "wasteful": avg_util < 30}
