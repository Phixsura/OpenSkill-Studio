"""Fleet GitLab CI — track pipeline performance."""
from __future__ import annotations
def fleet_gitlab_ci(pipelines: list[dict]) -> dict:
    success = [p for p in pipelines if p.get("status") == "success"]
    failed = [p for p in pipelines if p.get("status") == "failed"]
    avg_dur = round(sum(p.get("duration_min", 0) for p in success) / max(len(success), 1), 1)
    return {"total": len(pipelines), "success": len(success), "failed": len(failed),
            "avg_duration_min": avg_dur, "reliable": len(failed) == 0}
