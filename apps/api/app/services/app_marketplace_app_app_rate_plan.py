"""Rate plan — API rate limit plan configuration."""

import html

PLANS = {
    "free": {"rpm": 60, "rpd": 1000, "burst": 10, "concurrent": 5},
    "starter": {"rpm": 300, "rpd": 10000, "burst": 30, "concurrent": 10},
    "pro": {"rpm": 1000, "rpd": 100000, "burst": 100, "concurrent": 50},
    "enterprise": {"rpm": 5000, "rpd": 1000000, "burst": 500, "concurrent": 200},
}


def get_rate_plan(*, plan_id: str) -> dict:
    plan = PLANS.get(plan_id)
    if not plan:
        return {"error": f"Unknown plan: {plan_id}"}
    return {"id": plan_id, **plan,
            "rpm_display": f"{plan['rpm']}/min",
            "rpd_display": f"{plan['rpd']:,}/day"}


def check_usage(*, plan_id: str, current_rpm: int, current_rpd: int) -> dict:
    plan = PLANS.get(plan_id, PLANS["free"])
    rpm_pct = round(current_rpm / max(plan["rpm"], 1) * 100, 1)
    rpd_pct = round(current_rpd / max(plan["rpd"], 1) * 100, 1)
    throttled = current_rpm >= plan["rpm"]
    return {"plan": plan_id, "rpm_usage_pct": rpm_pct, "rpd_usage_pct": rpd_pct,
            "throttled": throttled, "upgrade_suggested": rpm_pct > 80 or rpd_pct > 80}
