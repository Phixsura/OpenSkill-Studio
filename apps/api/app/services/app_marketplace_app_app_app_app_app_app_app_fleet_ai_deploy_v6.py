"""Fleet AI Deploy v6 — track ultimate zero-downtime deployment."""
from __future__ import annotations
def fleet_ai_deploy_v6(deployers: list[dict]) -> dict:
    active = [d for d in deployers if d.get("active", True)]
    deploys = sum(d.get("deploys_24h", 0) for d in deployers)
    rollbacks = sum(d.get("rollbacks", 0) for d in deployers)
    lead_min = round(sum(d.get("lead_min", 0) for d in deployers) / max(len(deployers), 1), 1)
    zero_dt = all(d.get("zero_dt", False) for d in deployers)
    return {"deployers": len(deployers), "active": len(active), "deploys": deploys,
            "rollbacks": rollbacks, "lead_min": lead_min, "zero_dt": zero_dt, "elite": lead_min < 10 and zero_dt}
