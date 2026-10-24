"""Fleet AI Tensor Compute — track distributed tensor computation."""
from __future__ import annotations
def fleet_ai_tensor_compute(clusters: list[dict]) -> dict:
    active = [c for c in clusters if c.get("active", True)]
    tflops = sum(c.get("tflops", 0) for c in clusters)
    jobs_24h = sum(c.get("jobs_24h", 0) for c in clusters)
    utilization = round(sum(c.get("util_pct", 0) for c in clusters) / max(len(clusters), 1), 1)
    return {"clusters": len(clusters), "active": len(active), "tflops": tflops,
            "jobs_24h": jobs_24h, "utilization": utilization, "efficient": utilization > 75}
