"""Fleet AI DORA v8 — track ultimate DORA metrics at hyperscale."""
from __future__ import annotations
def fleet_ai_dora_v8(trackers: list[dict]) -> dict:
    freq = round(sum(t.get("freq_day", 0) for t in trackers) / max(len(trackers), 1), 1)
    lead = round(sum(t.get("lead_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    fail = round(sum(t.get("fail_pct", 0) for t in trackers) / max(len(trackers), 1), 2)
    mttr = round(sum(t.get("mttr_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    elite = freq > 1 and lead < 60 and fail < 5 and mttr < 60
    return {"freq": freq, "lead": lead, "fail": fail, "mttr": mttr,
            "class": "Elite" if elite else "High", "elite": elite}
