"""Billing summary — invoice and subscription summary."""

import html
from datetime import datetime, timezone


def build_billing_summary(*, plan: dict, usage: list[dict], invoices: list[dict]) -> dict:
    total_charges = sum(i.get("amount", 0) for i in invoices)
    current_usage = sum(u.get("cost", 0) for u in usage)
    return {
        "plan": {
            "name": html.escape(plan.get("name", "Free")),
            "price": plan.get("price", 0),
            "interval": plan.get("interval", "monthly"),
            "status": plan.get("status", "active"),
        },
        "current_usage": round(current_usage, 2),
        "usage_items": [{"name": html.escape(u.get("name", "")),
                          "quantity": u.get("quantity", 0),
                          "unit_price": u.get("unit_price", 0),
                          "cost": round(u.get("cost", 0), 2)} for u in usage],
        "invoices": [{"id": i["id"], "amount": i["amount"],
                       "status": i.get("status", "paid"),
                       "date": i.get("date", "")} for i in invoices[-5:]],
        "total_charges": round(total_charges, 2),
    }
