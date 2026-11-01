"""Fleet OOM tracker — track out-of-memory kills."""
from __future__ import annotations
def fleet_oom_tracker(pods: list[dict]) -> dict:
    oom_killed = [p for p in pods if p.get("oom_killed", False)]
    total_ooms = sum(p.get("oom_count", 0) for p in pods)
    return {"total": len(pods), "oom_pods": len(oom_killed), "total_ooms": total_ooms,
            "healthy": total_ooms == 0}
