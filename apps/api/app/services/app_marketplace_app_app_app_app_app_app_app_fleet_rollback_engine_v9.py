"""Fleet Rollback Engine v9 — track deployment rollback history."""
from __future__ import annotations
def fleet_rollback_engine_v9(rollbacks: list[dict]) -> dict:
    auto = [r for r in rollbacks if r.get("type") == "auto"]
    manual = [r for r in rollbacks if r.get("type") == "manual"]
    avg_time = sum(r.get("duration_sec", 0) for r in rollbacks) / len(rollbacks) if rollbacks else 0
    return {"total": len(rollbacks), "auto": len(auto), "manual": len(manual),
            "avg_rollback_sec": round(avg_time, 1), "healthy": avg_time < 300}
