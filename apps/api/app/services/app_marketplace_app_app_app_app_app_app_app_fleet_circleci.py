"""Fleet CircleCI — track workflow metrics."""
from __future__ import annotations
def fleet_circleci_status(workflows: list[dict]) -> dict:
    success = [w for w in workflows if w.get("status") == "success"]
    credits_used = sum(w.get("credits", 0) for w in workflows)
    return {"total": len(workflows), "success": len(success),
            "credits_used": credits_used, "success_rate": round(len(success) / max(len(workflows), 1) * 100, 1)}
