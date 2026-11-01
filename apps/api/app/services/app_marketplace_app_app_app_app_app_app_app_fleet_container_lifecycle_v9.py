"""Fleet Container Lifecycle v9 — track container image pull, run, stop."""
from __future__ import annotations
def fleet_container_lifecycle_v9(containers: list[dict]) -> dict:
    running = [c for c in containers if c.get("phase") == "running"]
    terminated = [c for c in containers if c.get("phase") == "terminated"]
    waiting = [c for c in containers if c.get("phase") == "waiting"]
    restarts = sum(c.get("restarts", 0) for c in containers)
    return {"containers": len(containers), "running": len(running), "terminated": len(terminated),
            "waiting": len(waiting), "restarts": restarts, "healthy": len(waiting) == 0 and restarts < 10}
