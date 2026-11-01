"""Fleet deployment lead time — commit to production time."""
from __future__ import annotations
def fleet_lead_time(deploys: list[dict]) -> dict:
    times = [d.get("lead_time_min", 0) for d in deploys]
    avg = round(sum(times) / max(len(times), 1), 1)
    under_hour = [t for t in times if t <= 60]
    return {"total": len(deploys), "avg_lead_time_min": avg,
            "under_hour": len(under_hour), "elite": avg <= 60}
