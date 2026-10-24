"""Fleet adoption curve — track platform adoption over time."""
from __future__ import annotations
def fleet_adoption_curve(months: list[dict]) -> dict:
    users = [m.get("active_users", 0) for m in months]
    growth = round((users[-1] - users[0]) / max(users[0], 1) * 100, 1) if len(users) >= 2 else 0
    return {"months": len(months), "current_users": users[-1] if users else 0,
            "growth_pct": growth, "accelerating": growth > 20}
