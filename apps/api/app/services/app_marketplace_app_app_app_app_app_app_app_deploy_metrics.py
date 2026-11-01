"""Deployment metrics — DORA four key metrics calculator."""
from __future__ import annotations


def calculate_dora_metrics(data: dict) -> dict:
    freq = data.get("deploy_frequency_per_day", 0)
    lead_time = data.get("lead_time_hours", 0)
    mttr = data.get("mttr_hours", 0)
    cfr = data.get("change_failure_rate_pct", 0)
    
    freq_level = "elite" if freq >= 1 else "high" if freq >= 1/7 else "medium" if freq >= 1/30 else "low"
    lead_level = "elite" if lead_time < 24 else "high" if lead_time < 168 else "medium" if lead_time < 720 else "low"
    mttr_level = "elite" if mttr < 1 else "high" if mttr < 24 else "medium" if mttr < 168 else "low"
    cfr_level = "elite" if cfr < 5 else "high" if cfr < 10 else "medium" if cfr < 15 else "low"
    
    levels = [freq_level, lead_level, mttr_level, cfr_level]
    rank_map = {"elite": 4, "high": 3, "medium": 2, "low": 1}
    avg_rank = sum(rank_map.get(l, 1) for l in levels) / 4
    overall = "elite" if avg_rank >= 3.5 else "high" if avg_rank >= 2.5 else "medium" if avg_rank >= 1.5 else "low"
    
    return {"deploy_frequency": {"value": freq, "level": freq_level},
            "lead_time": {"value": lead_time, "level": lead_level},
            "mttr": {"value": mttr, "level": mttr_level},
            "change_failure_rate": {"value": cfr, "level": cfr_level},
            "overall": overall}
