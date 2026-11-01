"""Subscription manager — manage app subscriptions and billing cycles."""

import secrets
from datetime import datetime, timedelta


def create_subscription(*, user_id: str, app_id: str, plan: str,
                          billing_cycle: str = "monthly") -> dict:
    valid_cycles = {"monthly", "yearly"}
    if billing_cycle not in valid_cycles:
        return {"error": f"Invalid cycle. Valid: {', '.join(sorted(valid_cycles))}"}
    now = datetime.utcnow()
    period_days = 30 if billing_cycle == "monthly" else 365
    return {
        "subscription_id": f"sub_{secrets.token_urlsafe(8)}",
        "user_id": user_id,
        "app_id": app_id,
        "plan": plan,
        "billing_cycle": billing_cycle,
        "status": "active",
        "current_period_start": now.isoformat(),
        "current_period_end": (now + timedelta(days=period_days)).isoformat(),
        "cancel_at_period_end": False,
    }


def cancel_subscription(*, subscription: dict, immediate: bool = False) -> dict:
    if immediate:
        return {**subscription, "status": "cancelled",
                "cancelled_at": datetime.utcnow().isoformat()}
    return {**subscription, "cancel_at_period_end": True,
            "status": "active", "cancellation_scheduled": True}


def get_subscription_metrics(*, subscriptions: list[dict]) -> dict:
    active = sum(1 for s in subscriptions if s.get("status") == "active")
    cancelled = sum(1 for s in subscriptions if s.get("status") == "cancelled")
    churn_rate = round(cancelled / max(active + cancelled, 1) * 100, 1)
    by_plan: dict[str, int] = {}
    for s in subscriptions:
        p = s.get("plan", "unknown")
        by_plan[p] = by_plan.get(p, 0) + 1
    return {"active": active, "cancelled": cancelled, "churn_rate": churn_rate,
            "by_plan": by_plan, "total": len(subscriptions)}
