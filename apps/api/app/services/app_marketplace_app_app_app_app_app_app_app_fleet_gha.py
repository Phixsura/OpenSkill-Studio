"""Fleet GitHub Actions — track workflow run metrics."""
from __future__ import annotations
def fleet_gha_status(workflows: list[dict]) -> dict:
    success = [w for w in workflows if w.get("conclusion") == "success"]
    failure = [w for w in workflows if w.get("conclusion") == "failure"]
    total_minutes = sum(w.get("billable_min", 0) for w in workflows)
    return {"total": len(workflows), "success": len(success), "failure": len(failure),
            "billable_minutes": total_minutes, "success_rate": round(len(success) / max(len(workflows), 1) * 100, 1)}
