"""Fleet Woodpecker CI — track pipeline execution."""
from __future__ import annotations
def fleet_woodpecker_status(pipelines: list[dict]) -> dict:
    success = [p for p in pipelines if p.get("status") == "success"]
    avg_dur = round(sum(p.get("duration_sec", 0) for p in success) / max(len(success), 1), 1)
    return {"total": len(pipelines), "success": len(success),
            "failed": len(pipelines) - len(success), "avg_sec": avg_dur}
