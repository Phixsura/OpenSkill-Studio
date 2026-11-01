"""Fleet graceful shutdown — track graceful termination compliance."""
from __future__ import annotations
def fleet_graceful_shutdown(pods: list[dict]) -> dict:
    graceful = [p for p in pods if p.get("graceful_shutdown", True)]
    forced = [p for p in pods if not p.get("graceful_shutdown", True)]
    return {"total": len(pods), "graceful": len(graceful), "forced_kill": len(forced),
            "compliant": len(forced) == 0}
