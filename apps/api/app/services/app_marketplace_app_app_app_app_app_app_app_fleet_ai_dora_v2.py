"""Fleet AI DORA Metrics v2 — track DORA performance classification."""
from __future__ import annotations
def fleet_ai_dora_metrics_v2(trackers: list[dict]) -> dict:
    deploy_freq = round(sum(t.get("deploy_freq_day", 0) for t in trackers) / max(len(trackers), 1), 1)
    lead_time_min = round(sum(t.get("lead_time_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    change_fail_pct = round(sum(t.get("fail_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    mttr_min = round(sum(t.get("mttr_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    elite = deploy_freq > 1 and lead_time_min < 60 and change_fail_pct < 5 and mttr_min < 60
    return {"deploy_freq": deploy_freq, "lead_time_min": lead_time_min, "fail_pct": change_fail_pct,
            "mttr_min": mttr_min, "classification": "Elite" if elite else "High", "elite": elite}
