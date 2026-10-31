"""Fleet executive summary — high-level platform KPIs."""
from __future__ import annotations
def fleet_exec_summary(kpis: dict) -> dict:
    uptime = kpis.get("uptime_pct", 99.9)
    deploy_freq = kpis.get("deploys_per_day", 0)
    mttr_min = kpis.get("mttr_minutes", 0)
    cfr = kpis.get("change_failure_rate_pct", 0)
    grade = "Elite" if uptime >= 99.99 and deploy_freq >= 10 and mttr_min < 60 and cfr < 5 else "High" if uptime >= 99.9 else "Medium"
    return {"uptime_pct": uptime, "deploy_freq": deploy_freq, "mttr_min": mttr_min,
            "cfr_pct": cfr, "dora_grade": grade}
