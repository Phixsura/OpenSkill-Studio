"""Fleet Resource Optimizer v9 — track resource right-sizing recommendations."""
from __future__ import annotations
def fleet_resource_optimizer_v9(recs: list[dict]) -> dict:
    applied = [r for r in recs if r.get("applied")]
    savings_monthly = sum(r.get("savings_monthly", 0) for r in recs)
    cpu_saved = sum(r.get("cpu_cores_saved", 0) for r in recs)
    return {"recommendations": len(recs), "applied": len(applied),
            "savings_monthly": round(savings_monthly, 2), "cpu_cores_saved": cpu_saved,
            "healthy": len(applied) > len(recs) * 0.5}
