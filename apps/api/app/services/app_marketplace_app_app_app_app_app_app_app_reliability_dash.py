"""Reliability engineering dashboard — comprehensive reliability view."""
from __future__ import annotations


def build_reliability_dashboard(data: dict) -> dict:
    mttr = data.get("mttr_min", 0)
    mtbf = data.get("mtbf_hours", 0)
    change_failure = data.get("change_failure_pct", 0)
    uptime = data.get("uptime_pct", 99.9)
    
    reliability_score = round(
        (min(uptime, 100) * 0.35) +
        (max(0, 100 - change_failure * 5) * 0.25) +
        (max(0, 100 - mttr) * 0.20) +
        (min(mtbf / 24 * 10, 100) * 0.20), 1)
    
    maturity = "advanced" if reliability_score >= 85 else "intermediate" if reliability_score >= 65 else "basic"
    return {"reliability_score": min(reliability_score, 100), "maturity": maturity,
            "mttr_min": mttr, "mtbf_hours": mtbf,
            "change_failure_pct": change_failure, "uptime_pct": uptime}
