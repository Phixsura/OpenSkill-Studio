"""App billing page — complete billing management page."""

import html


def build_billing_page(*, org: dict, plan: dict, usage: dict,
                         invoices: list[dict], payment: dict | None = None) -> dict:
    overage = max(0, usage.get("api_calls", 0) - plan.get("api_limit", 0)) * plan.get("overage_rate", 0.001)
    monthly = plan.get("price", 0) + round(overage, 2)
    return {
        "org_name": html.escape(org.get("name", "")),
        "plan": {"name": plan.get("name", "Free"), "price": plan.get("price", 0),
                  "interval": plan.get("interval", "monthly"),
                  "api_limit": plan.get("api_limit", 0)},
        "usage": {"api_calls": usage.get("api_calls", 0),
                   "api_pct": round(usage.get("api_calls", 0) / max(plan.get("api_limit", 1), 1) * 100, 1),
                   "storage_mb": usage.get("storage_mb", 0)},
        "billing": {"base": plan.get("price", 0), "overage": round(overage, 2),
                      "total": round(monthly, 2)},
        "payment": {"brand": html.escape(payment.get("brand", "")),
                      "last4": payment.get("last4", "")} if payment else None,
        "invoices": [{"id": i.get("id", ""), "amount": i.get("amount", 0),
                       "status": i.get("status", "paid"), "date": i.get("date", "")}
                      for i in invoices[:5]],
    }
