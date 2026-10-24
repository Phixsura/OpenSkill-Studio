"""Fleet Pod Lifecycle v9 — track pod creation, running, and termination."""
from __future__ import annotations
def fleet_pod_lifecycle_v9(pods: list[dict]) -> dict:
    running = [p for p in pods if p.get("phase") == "Running"]
    pending = [p for p in pods if p.get("phase") == "Pending"]
    failed = [p for p in pods if p.get("phase") == "Failed"]
    restarts = sum(p.get("restarts", 0) for p in pods)
    return {"pods": len(pods), "running": len(running), "pending": len(pending),
            "failed": len(failed), "restarts": restarts, "healthy": len(failed) == 0}
