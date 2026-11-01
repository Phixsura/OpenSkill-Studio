"""Fleet OpsGenie — track alert management health."""
from __future__ import annotations
def fleet_opsgenie_status(teams: list[dict]) -> dict:
    open_alerts = sum(t.get("open_alerts", 0) for t in teams)
    avg_close_min = round(sum(t.get("avg_close_min", 0) for t in teams) / max(len(teams), 1), 1)
    on_call = [t for t in teams if t.get("has_on_call", True)]
    return {"teams": len(teams), "open_alerts": open_alerts, "avg_close_min": avg_close_min,
            "with_on_call": len(on_call), "responsive": avg_close_min < 30}
