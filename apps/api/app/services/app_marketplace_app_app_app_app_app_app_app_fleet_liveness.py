"""Fleet liveness probe — track liveness probe failures."""
from __future__ import annotations
def fleet_liveness_probes(pods: list[dict]) -> dict:
    failing = [p for p in pods if p.get("liveness_failures", 0) > 0]
    total_failures = sum(p.get("liveness_failures", 0) for p in pods)
    return {"total": len(pods), "failing_pods": len(failing),
            "total_failures": total_failures, "healthy": len(failing) == 0}
