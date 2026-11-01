"""SLA monitor — track SLA compliance for premium apps."""

from datetime import datetime, timezone


def define_sla(*, app_id: str, uptime_target: float, response_time_target_ms: int,
                 support_response_hours: int) -> dict:
    if uptime_target < 90 or uptime_target > 100:
        return {"error": "Uptime target must be between 90% and 100%"}
    return {
        "app_id": app_id, "uptime_target": uptime_target,
        "response_time_target_ms": response_time_target_ms,
        "support_response_hours": support_response_hours, "error": None,
    }


def check_sla_compliance(*, sla: dict, actual_uptime: float, actual_response_ms: int,
                            actual_support_hours: float) -> dict:
    checks = {
        "uptime": {"target": sla["uptime_target"], "actual": actual_uptime,
                    "met": actual_uptime >= sla["uptime_target"]},
        "response_time": {"target": sla["response_time_target_ms"], "actual": actual_response_ms,
                           "met": actual_response_ms <= sla["response_time_target_ms"]},
        "support": {"target": sla["support_response_hours"], "actual": actual_support_hours,
                     "met": actual_support_hours <= sla["support_response_hours"]},
    }
    all_met = all(c["met"] for c in checks.values())
    return {"compliant": all_met, "checks": checks, "checked_at": datetime.now(timezone.utc).isoformat()}


def calculate_sla_credits(*, sla: dict, actual_uptime: float, monthly_fee: int) -> dict:
    if actual_uptime >= sla["uptime_target"]:
        return {"credit_pct": 0, "credit_amount": 0}
    shortfall = sla["uptime_target"] - actual_uptime
    credit_pct = min(50, round(shortfall * 10))
    return {"credit_pct": credit_pct, "credit_amount": round(monthly_fee * credit_pct / 100)}
