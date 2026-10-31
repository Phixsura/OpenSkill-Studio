"""Fleet Compute Optimizer v9 — track compute instance right-sizing."""
from __future__ import annotations
def fleet_compute_optimizer_v9(instances: list[dict]) -> dict:
    oversized = [i for i in instances if i.get("recommendation") == "downsize"]
    undersized = [i for i in instances if i.get("recommendation") == "upsize"]
    optimal = [i for i in instances if i.get("recommendation") == "optimal"]
    savings = sum(i.get("monthly_savings", 0) for i in oversized)
    return {"instances": len(instances), "oversized": len(oversized), "undersized": len(undersized),
            "optimal": len(optimal), "potential_savings": round(savings, 2), "healthy": True}
