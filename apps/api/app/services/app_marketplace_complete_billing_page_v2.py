"""Complete billing page v2 — comprehensive billing management with invoices, usage, and plan comparison."""


def build_complete_billing_page_v2(*, developer: dict, current_plan: dict, usage: dict,
                                       invoices: list[dict], payment_method: dict | None,
                                       cost_breakdown: dict, plan_options: list[dict]) -> dict:
    past_due = any(i.get("status") == "past_due" for i in invoices)
    current_spend = sum(i.get("amount_cents", 0) for i in invoices if i.get("period") == usage.get("current_period"))
    return {
        "page_type": "billing_v2",
        "plan": {"name": current_plan.get("name", "free"), "price": current_plan.get("price_label", "Free"),
                  "renewal_date": current_plan.get("renewal_date"),
                  "features_used": current_plan.get("features_used", 0),
                  "features_total": current_plan.get("features_total", 0)},
        "usage_summary": usage,
        "cost": {"current_spend_cents": current_spend, "current_spend": f"${current_spend / 100:,.2f}",
                  "breakdown": cost_breakdown},
        "payment": {"has_method": payment_method is not None,
                      "type": payment_method.get("type") if payment_method else None,
                      "last_four": payment_method.get("last_four") if payment_method else None},
        "invoices": {"recent": invoices[:10], "total": len(invoices), "past_due": past_due},
        "upgrade_options": plan_options,
        "alerts": {"past_due": past_due, "near_limit": usage.get("usage_pct", 0) > 80},
    }
