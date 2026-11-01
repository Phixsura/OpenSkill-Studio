"""Developer billing portal — unified billing management for developers."""

from datetime import datetime, timezone


def get_billing_overview(*, plan: dict, usage: dict, invoices: list[dict]) -> dict:
    current_spend = sum(i.get("amount_cents", 0) for i in invoices if i.get("status") == "paid")
    return {
        "plan": plan, "current_spend_cents": current_spend,
        "current_spend": f"${current_spend / 100:,.2f}",
        "usage_summary": usage, "invoice_count": len(invoices),
        "next_billing": plan.get("next_billing_date"),
    }


def generate_invoice_preview(*, plan_price: int, overages: dict) -> dict:
    overage_total = sum(overages.values())
    total = plan_price + overage_total
    return {"plan_price_cents": plan_price, "overages": overages,
            "overage_total_cents": overage_total, "total_cents": total,
            "total": f"${total / 100:,.2f}"}


def get_plan_comparison(*, current_plan: str) -> list[dict]:
    plans = [
        {"name": "Free", "price": 0, "features": ["1 app", "1K API calls", "Community support"]},
        {"name": "Starter", "price": 2900, "features": ["5 apps", "100K API calls", "Email support"]},
        {"name": "Pro", "price": 9900, "features": ["Unlimited apps", "1M API calls", "Priority support", "Analytics"]},
        {"name": "Enterprise", "price": -1, "features": ["Custom limits", "Dedicated support", "SLA", "SSO"]},
    ]
    for p in plans:
        p["current"] = p["name"].lower() == current_plan.lower()
    return plans
