"""Fleet init containers — track init container success rates."""
from __future__ import annotations
def fleet_init_containers(pods: list[dict]) -> dict:
    with_init = [p for p in pods if p.get("has_init_containers", False)]
    failed_init = [p for p in pods if p.get("init_failed", False)]
    return {"total": len(pods), "with_init": len(with_init), "failed_init": len(failed_init),
            "healthy": len(failed_init) == 0}
