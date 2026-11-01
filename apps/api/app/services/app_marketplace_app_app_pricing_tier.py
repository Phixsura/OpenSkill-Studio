"""Pricing tier — plan comparison and pricing calculator."""

import html

PLANS = {
    "free": {"price": 0, "interval": "forever", "features": ["5 apps", "1K API calls/mo", "Community support"]},
    "starter": {"price": 9, "interval": "monthly", "features": ["25 apps", "50K API calls/mo", "Email support", "Custom domain"]},
    "pro": {"price": 29, "interval": "monthly", "features": ["Unlimited apps", "500K API calls/mo", "Priority support", "Custom domain", "Analytics", "Webhooks"]},
    "enterprise": {"price": 99, "interval": "monthly", "features": ["Unlimited everything", "SLA", "Dedicated support", "SSO", "Audit logs", "Custom integrations"]},
}


def get_plan(*, plan_id: str) -> dict:
    plan = PLANS.get(plan_id)
    if not plan:
        return {"error": f"Unknown plan: {plan_id}"}
    return {"id": plan_id, **plan, "feature_count": len(plan["features"])}


def compare_plans() -> dict:
    items = [{"id": k, **v, "feature_count": len(v["features"]),
              "recommended": k == "pro"} for k, v in PLANS.items()]
    return {"plans": items, "total": len(items)}


def calculate_annual(*, monthly_price: float, discount_pct: int = 20) -> dict:
    annual = monthly_price * 12
    discounted = round(annual * (1 - discount_pct / 100), 2)
    savings = round(annual - discounted, 2)
    return {"monthly": monthly_price, "annual": annual, "annual_discounted": discounted,
            "monthly_equivalent": round(discounted / 12, 2), "savings": savings}
