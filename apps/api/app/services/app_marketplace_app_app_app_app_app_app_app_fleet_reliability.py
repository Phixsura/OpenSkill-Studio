"""Fleet reliability score — composite reliability metric."""
from __future__ import annotations
def fleet_reliability_score(metrics: dict) -> dict:
    uptime = metrics.get("uptime_pct", 99.9)
    mttr = metrics.get("mttr_min", 60)
    cfr = metrics.get("cfr_pct", 5)
    score = round(uptime - (mttr / 60) - (cfr * 2), 2)
    grade = "Platinum" if score >= 97 else ("Gold" if score >= 95 else ("Silver" if score >= 90 else "Bronze"))
    return {"score": score, "grade": grade, "uptime": uptime, "mttr_min": mttr, "cfr_pct": cfr}
