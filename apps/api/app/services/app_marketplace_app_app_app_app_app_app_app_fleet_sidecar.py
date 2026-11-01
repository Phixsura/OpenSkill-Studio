"""Fleet sidecar injection — track sidecar proxy injection status."""
from __future__ import annotations
def fleet_sidecar_status(pods: list[dict]) -> dict:
    injected = [p for p in pods if p.get("sidecar_injected", False)]
    pct = round(len(injected) / max(len(pods), 1) * 100, 1)
    return {"total": len(pods), "injected": len(injected), "missing": len(pods) - len(injected),
            "coverage_pct": pct, "full": pct == 100}
