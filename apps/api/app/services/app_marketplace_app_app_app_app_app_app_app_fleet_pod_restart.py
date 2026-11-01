"""Fleet pod restart tracker — monitor restart counts across pods."""
from __future__ import annotations
def fleet_pod_restarts(pods: list[dict]) -> dict:
    total = sum(p.get("restarts", 0) for p in pods)
    crashlooping = [p for p in pods if p.get("restarts", 0) >= 5]
    return {"total_restarts": total, "crashlooping": len(crashlooping),
            "pods": len(pods), "stable": len(crashlooping) == 0}
