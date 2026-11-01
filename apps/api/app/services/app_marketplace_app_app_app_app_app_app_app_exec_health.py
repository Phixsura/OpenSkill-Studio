"""Executive health report — one-page platform health for leadership."""
from __future__ import annotations


def generate_exec_report(data: dict) -> dict:
    uptime = data.get("uptime_pct", 99.9)
    revenue = data.get("revenue", 0)
    users = data.get("users", 0)
    deploys = data.get("deploys_week", 0)
    incidents = data.get("incidents_month", 0)
    mttr = data.get("mttr_min", 0)
    score = round(uptime * 0.3 + (100 - incidents) * 0.2 + min(deploys / 5, 1) * 100 * 0.2 + max(0, 100 - mttr) * 0.15 + min(users / 1000, 1) * 100 * 0.15)
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D"
    return {"score": min(score, 100), "grade": grade,
            "kpis": {"uptime": f"{uptime}%", "revenue": f"${revenue:,}", "users": f"{users:,}",
                      "deploys_week": deploys, "incidents": incidents, "mttr_min": mttr},
            "status": "excellent" if grade == "A" else "good" if grade == "B" else "needs_attention"}
