"""Fleet API Error Budget v9 — track per-API error budget consumption."""
from __future__ import annotations
def fleet_api_error_budget_v9(apis: list[dict]) -> dict:
    burning = [a for a in apis if a.get("burn_rate", 0) > 1.0]
    exhausted = [a for a in apis if a.get("budget_remaining", 100) <= 0]
    avg_remaining = sum(a.get("budget_remaining", 100) for a in apis) / len(apis) if apis else 0
    return {"apis": len(apis), "burning_fast": len(burning), "exhausted": len(exhausted),
            "avg_remaining_pct": round(avg_remaining, 1), "healthy": len(exhausted) == 0}
