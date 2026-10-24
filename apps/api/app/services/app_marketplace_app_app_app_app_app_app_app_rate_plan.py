"""API rate plan manager — manage tiered API rate plans."""
from __future__ import annotations


PLANS = {
    "free": {"rpm": 60, "daily": 1000, "monthly": 10000},
    "starter": {"rpm": 300, "daily": 10000, "monthly": 100000},
    "pro": {"rpm": 1000, "daily": 100000, "monthly": 1000000},
    "enterprise": {"rpm": 10000, "daily": 1000000, "monthly": 10000000},
}


def get_plan(plan_name: str) -> dict:
    plan = PLANS.get(plan_name)
    if not plan:
        return {"found": False, "plan": plan_name}
    return {"found": True, "plan": plan_name, "limits": plan}


def check_usage(plan_name: str, current_daily: int, current_monthly: int) -> dict:
    plan = PLANS.get(plan_name, PLANS["free"])
    daily_pct = round(current_daily / max(plan["daily"], 1) * 100, 1)
    monthly_pct = round(current_monthly / max(plan["monthly"], 1) * 100, 1)
    exceeded = current_daily > plan["daily"] or current_monthly > plan["monthly"]
    recommend_upgrade = daily_pct > 80 or monthly_pct > 80
    return {"plan": plan_name, "daily_pct": daily_pct, "monthly_pct": monthly_pct,
            "exceeded": exceeded, "recommend_upgrade": recommend_upgrade}
