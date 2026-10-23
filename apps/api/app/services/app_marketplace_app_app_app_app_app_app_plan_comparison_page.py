"""Plan comparison page — detailed plan comparison with all features."""

PLANS = [
    {"id": "free", "name": "Free", "price": 0, "billing": "forever", "cta": "Get Started"},
    {"id": "starter", "name": "Starter", "price": 9, "billing": "monthly", "cta": "Start Free Trial"},
    {"id": "pro", "name": "Pro", "price": 29, "billing": "monthly", "cta": "Start Free Trial", "recommended": True},
    {"id": "enterprise", "name": "Enterprise", "price": -1, "billing": "custom", "cta": "Contact Sales"},
]

FEATURES = [
    {"name": "Apps", "free": "5", "starter": "25", "pro": "Unlimited", "enterprise": "Unlimited"},
    {"name": "API Calls/mo", "free": "1,000", "starter": "50,000", "pro": "500,000", "enterprise": "Unlimited"},
    {"name": "Webhooks", "free": "2", "starter": "10", "pro": "50", "enterprise": "Unlimited"},
    {"name": "Team Members", "free": "1", "starter": "5", "pro": "25", "enterprise": "Unlimited"},
    {"name": "Custom Domain", "free": False, "starter": True, "pro": True, "enterprise": True},
    {"name": "Analytics", "free": False, "starter": "Basic", "pro": "Advanced", "enterprise": "Custom"},
    {"name": "Webhooks", "free": False, "starter": True, "pro": True, "enterprise": True},
    {"name": "Priority Support", "free": False, "starter": False, "pro": True, "enterprise": True},
    {"name": "SSO/SAML", "free": False, "starter": False, "pro": False, "enterprise": True},
    {"name": "SLA", "free": False, "starter": False, "pro": False, "enterprise": "99.99%"},
    {"name": "Audit Logs", "free": False, "starter": False, "pro": True, "enterprise": True},
]


def build_plan_comparison_page() -> dict:
    plans = []
    for p in PLANS:
        price_display = "Free" if p["price"] == 0 else "Custom" if p["price"] < 0 else f"${p['price']}/mo"
        plans.append({**p, "price_display": price_display})
    features = []
    for f in FEATURES:
        row = {"name": f["name"], "values": {}}
        for p in PLANS:
            val = f.get(p["id"])
            if isinstance(val, bool):
                row["values"][p["id"]] = {"display": "✓" if val else "✗", "type": "bool", "value": val}
            else:
                row["values"][p["id"]] = {"display": str(val) if val else "✗", "type": "text", "value": val}
        features.append(row)
    return {"plans": plans, "features": features, "plan_count": len(plans), "feature_count": len(features)}
