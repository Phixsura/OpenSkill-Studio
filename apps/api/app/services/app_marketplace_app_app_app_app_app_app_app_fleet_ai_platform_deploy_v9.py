"""Fleet AI Deploy v9 — track ultimate deployment at planetary scale."""
from __future__ import annotations
def fleet_ai_deploy_v9(deployers: list[dict]) -> dict:
    active = [d for d in deployers if d.get("active", True)]
    deploys = sum(d.get("deploys_24h", 0) for d in deployers)
    lead = round(sum(d.get("lead_min", 0) for d in deployers) / max(len(deployers), 1), 1)
    zero_dt = all(d.get("zero_dt", False) for d in deployers)
    return {"deployers": len(deployers), "active": len(active), "deploys": deploys,
            "lead": lead, "zero_dt": zero_dt, "instant": lead < 2}
