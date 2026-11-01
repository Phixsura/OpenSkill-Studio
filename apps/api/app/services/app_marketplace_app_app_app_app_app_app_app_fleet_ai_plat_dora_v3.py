"""Fleet AI DORA v3 — track ultimate DORA metrics with trends."""
from __future__ import annotations
def fleet_ai_dora_v3(trackers: list[dict]) -> dict:
    deploy_freq = round(sum(t.get("freq_day", 0) for t in trackers) / max(len(trackers), 1), 1)
    lead_time = round(sum(t.get("lead_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    fail_rate = round(sum(t.get("fail_pct", 0) for t in trackers) / max(len(trackers), 1), 2)
    mttr = round(sum(t.get("mttr_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    trend = "improving" if all(t.get("improving", False) for t in trackers) else "stable"
    elite = deploy_freq > 1 and lead_time < 60 and fail_rate < 5 and mttr < 60
    return {"freq": deploy_freq, "lead_min": lead_time, "fail_pct": fail_rate,
            "mttr_min": mttr, "trend": trend, "classification": "Elite" if elite else "High"}
