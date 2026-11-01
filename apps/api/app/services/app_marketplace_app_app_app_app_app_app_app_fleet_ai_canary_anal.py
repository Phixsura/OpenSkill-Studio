"""Fleet AI Canary Analysis — track automated canary deployment analysis."""
from __future__ import annotations
def fleet_ai_canary_analysis(analyzers: list[dict]) -> dict:
    active = [a for a in analyzers if a.get("active", True)]
    analyses_24h = sum(a.get("analyses_24h", 0) for a in analyzers)
    promoted = sum(a.get("promoted", 0) for a in analyzers)
    rolled_back = sum(a.get("rolled_back", 0) for a in analyzers)
    return {"analyzers": len(analyzers), "active": len(active), "analyses_24h": analyses_24h,
            "promoted": promoted, "rolled_back": rolled_back, "safe": rolled_back == 0}
