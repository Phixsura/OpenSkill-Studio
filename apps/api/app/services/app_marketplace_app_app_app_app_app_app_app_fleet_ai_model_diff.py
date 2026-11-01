"""Fleet AI Model Diff — track model weight and behavior differences."""
from __future__ import annotations
def fleet_ai_model_diff(differs: list[dict]) -> dict:
    active = [d for d in differs if d.get("active", True)]
    diffs_24h = sum(d.get("diffs_24h", 0) for d in differs)
    regressions_found = sum(d.get("regressions", 0) for d in differs)
    improvements = sum(d.get("improvements", 0) for d in differs)
    return {"differs": len(differs), "active": len(active), "diffs_24h": diffs_24h,
            "regressions": regressions_found, "improvements": improvements, "insightful": diffs_24h > 0}
