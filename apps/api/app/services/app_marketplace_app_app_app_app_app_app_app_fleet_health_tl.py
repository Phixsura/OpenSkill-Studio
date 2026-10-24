"""Fleet health timeline — historical health snapshots."""
from __future__ import annotations
def fleet_health_timeline(snapshots: list[dict]) -> dict:
    scores = [s.get("score", 0) for s in snapshots]
    avg = round(sum(scores) / max(len(scores), 1), 1)
    trend = "improving" if len(scores) >= 2 and scores[-1] > scores[0] else "stable"
    best = max(scores) if scores else 0
    worst = min(scores) if scores else 0
    return {"snapshots": len(snapshots), "avg_score": avg, "best": best, "worst": worst, "trend": trend}
