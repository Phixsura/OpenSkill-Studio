"""Org billing — organization billing overview."""

import html
from datetime import datetime, timezone


def build_billing_overview(*, plan: dict, usage: dict, invoices: list[dict],
                             payment_method: dict | None = None) -> dict:
    monthly_total = plan.get("price", 0) + usage.get("overage", 0)
    return {
        "plan": {"name": plan.get("name", "Free"), "price": plan.get("price", 0),
                 "interval": plan.get("interval", "monthly")},
        "current_period": {
            "base_cost": plan.get("price", 0),
            "overage": usage.get("overage", 0),
            "total": round(monthly_total, 2),
        },
        "usage_summary": {
            "api_calls": usage.get("api_calls", 0),
            "api_limit": usage.get("api_limit", 0),
            "api_pct": round(usage.get("api_calls", 0) / max(usage.get("api_limit", 1), 1) * 100, 1),
            "storage_mb": usage.get("storage_mb", 0),
        },
        "payment_method": {
            "type": payment_method.get("type", "card") if payment_method else None,
            "last4": payment_method.get("last4", "") if payment_method else None,
            "brand": html.escape(payment_method.get("brand", "")) if payment_method else None,
        } if payment_method else None,
        "recent_invoices": invoices[:5],
        "has_payment_method": payment_method is not None,
    }
