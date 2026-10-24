"""Fleet operations summary — unified ops view."""
from __future__ import annotations
def fleet_ops_summary(stats: dict) -> dict:
    incidents_open = stats.get("incidents_open", 0)
    deploys_today = stats.get("deploys_today", 0)
    alerts_firing = stats.get("alerts_firing", 0)
    status = "calm" if incidents_open == 0 and alerts_firing == 0 else ("busy" if incidents_open <= 2 else "storm")
    return {"incidents_open": incidents_open, "deploys_today": deploys_today,
            "alerts_firing": alerts_firing, "status": status}
