"""Fleet AI Deploy v8 — track ultimate zero-downtime deployment."""
from __future__ import annotations
def fleet_ai_deploy_v8(deployers: list[dict]) -> dict:
    active = [d for d in deployers if d.get("active", True)]
    deploys = sum(d.get("deploys_24h", 0) for d in deployers)
    lead_min = round(sum(d.get("lead_min", 0) for d in deployers) / max(len(deployers), 1), 1)
    zero_dt = all(d.get("zero_dt", False) for d in deployers)
    return {"deployers": len(deployers), "active": len(active), "deploys": deploys,
            "lead_min": lead_min, "zero_dt": zero_dt, "instant": lead_min < 5 and zero_dt}
