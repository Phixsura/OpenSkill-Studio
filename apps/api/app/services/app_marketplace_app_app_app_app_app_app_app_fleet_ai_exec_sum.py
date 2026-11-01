"""Fleet AI Executive Summary — track C-suite AI platform overview."""
from __future__ import annotations
def fleet_ai_executive_summary(summaries: list[dict]) -> dict:
    revenue_usd = round(sum(s.get("revenue_usd", 0) for s in summaries), 2)
    cost_usd = round(sum(s.get("cost_usd", 0) for s in summaries), 2)
    margin_pct = round((revenue_usd - cost_usd) / max(revenue_usd, 1) * 100, 1)
    users = sum(s.get("users", 0) for s in summaries)
    uptime = round(sum(s.get("uptime_pct", 0) for s in summaries) / max(len(summaries), 1), 3)
    return {"revenue_usd": revenue_usd, "cost_usd": cost_usd, "margin_pct": margin_pct,
            "users": users, "uptime": uptime, "profitable": margin_pct > 50}
