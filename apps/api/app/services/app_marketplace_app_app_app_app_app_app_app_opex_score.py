"""Operational excellence scorecard — DORA + platform maturity metrics."""
from __future__ import annotations


def calculate_opex_score(dora: dict, platform: dict) -> dict:
    # DORA metrics scoring
    freq_score = 100 if dora.get("deploy_freq_per_day", 0) >= 1 else 75 if dora.get("deploy_freq_per_day", 0) >= 0.14 else 50
    lead_score = 100 if dora.get("lead_time_hours", 999) < 24 else 75 if dora.get("lead_time_hours", 999) < 168 else 50
    mttr_score = 100 if dora.get("mttr_hours", 999) < 1 else 75 if dora.get("mttr_hours", 999) < 24 else 50
    cfr_score = 100 if dora.get("change_failure_rate", 100) < 5 else 75 if dora.get("change_failure_rate", 100) < 15 else 50

    dora_score = round((freq_score + lead_score + mttr_score + cfr_score) / 4)
    platform_score = round((platform.get("automation_pct", 0) + platform.get("test_coverage", 0) +
                             platform.get("doc_coverage", 0)) / 3)
    overall = round(dora_score * 0.6 + platform_score * 0.4)
    level = "elite" if overall >= 90 else "high" if overall >= 75 else "medium" if overall >= 50 else "low"
    return {"dora_score": dora_score, "platform_score": platform_score,
            "overall": overall, "level": level,
            "dora_breakdown": {"frequency": freq_score, "lead_time": lead_score,
                                "mttr": mttr_score, "change_failure": cfr_score}}
