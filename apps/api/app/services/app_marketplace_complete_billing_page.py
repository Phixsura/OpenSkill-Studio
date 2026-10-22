"""Complete billing page — master aggregator for developer billing dashboard."""


def build_complete_billing_page(*, developer: dict, current_plan: dict, usage: dict,
                                   invoices: list[dict], cost_estimate: dict) -> dict:
    return {
        "page_type": "billing_dashboard",
        "developer": {"name": developer.get("display_name")},
        "plan": {"name": current_plan.get("name"), "price": current_plan.get("price"),
                  "renewal_date": current_plan.get("renewal_date")},
        "sections": [
            {"key": "overview", "title": "Billing Overview", "icon": "💳"},
            {"key": "usage", "title": "Current Usage", "icon": "📊", "data": usage},
            {"key": "estimate", "title": "Cost Estimate", "icon": "💰", "data": cost_estimate},
            {"key": "invoices", "title": f"Invoices ({len(invoices)})", "icon": "📄",
             "data": {"recent": invoices[:5]}},
            {"key": "plan", "title": "Plan & Upgrade", "icon": "⬆️"},
        ],
    }
