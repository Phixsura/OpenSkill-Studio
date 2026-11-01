"""Fleet API Rate Control v9 — track adaptive rate control policies."""
from __future__ import annotations
def fleet_api_rate_control_v9(policies: list[dict]) -> dict:
    adaptive = [p for p in policies if p.get("adaptive")]
    fixed = [p for p in policies if not p.get("adaptive")]
    throttled = sum(p.get("throttled_today", 0) for p in policies)
    return {"policies": len(policies), "adaptive": len(adaptive), "fixed": len(fixed),
            "throttled_today": throttled, "healthy": True}
