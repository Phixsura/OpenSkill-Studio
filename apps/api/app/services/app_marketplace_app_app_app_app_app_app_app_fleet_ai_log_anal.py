"""Fleet AI Log Analysis — track AI-powered log parsing and insights."""
from __future__ import annotations
def fleet_ai_log_analysis(analyzers: list[dict]) -> dict:
    active = [a for a in analyzers if a.get("active", True)]
    logs_24h = sum(a.get("logs_24h", 0) for a in analyzers)
    patterns_found = sum(a.get("patterns", 0) for a in analyzers)
    insights = sum(a.get("insights", 0) for a in analyzers)
    return {"analyzers": len(analyzers), "active": len(active), "logs_24h": logs_24h,
            "patterns": patterns_found, "insights": insights, "insightful": insights > 0}
