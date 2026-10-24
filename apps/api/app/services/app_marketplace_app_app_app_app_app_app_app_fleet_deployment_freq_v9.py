"""Fleet Deployment Frequency v9 — track DORA deployment frequency metric."""
from __future__ import annotations
def fleet_deployment_freq_v9(teams: list[dict]) -> dict:
    deploys_today = sum(t.get("deploys_today", 0) for t in teams)
    avg_per_day = sum(t.get("avg_per_day", 0) for t in teams) / len(teams) if teams else 0
    on_demand = [t for t in teams if t.get("on_demand")]
    return {"teams": len(teams), "deploys_today": deploys_today,
            "avg_per_day": round(avg_per_day, 1), "on_demand": len(on_demand),
            "dora_class": "Elite" if avg_per_day >= 1 else "High", "healthy": True}
