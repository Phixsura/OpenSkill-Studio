"""Pricing comparison — compare all plan features side by side."""

PLANS = [
    {"id": "free", "name": "Free", "price": 0, "billing": "forever"},
    {"id": "starter", "name": "Starter", "price": 9, "billing": "monthly"},
    {"id": "pro", "name": "Pro", "price": 29, "billing": "monthly", "recommended": True},
    {"id": "enterprise", "name": "Enterprise", "price": -1, "billing": "custom"},
]

FEATURES = [
    {"name": "Apps", "values": {"free": "5", "starter": "25", "pro": "Unlimited", "enterprise": "Unlimited"}},
    {"name": "API Calls/mo", "values": {"free": "1K", "starter": "50K", "pro": "500K", "enterprise": "Unlimited"}},
    {"name": "Team Members", "values": {"free": "1", "starter": "5", "pro": "25", "enterprise": "Unlimited"}},
    {"name": "Webhooks", "values": {"free": "2", "starter": "10", "pro": "50", "enterprise": "Unlimited"}},
    {"name": "Custom Domain", "values": {"free": False, "starter": True, "pro": True, "enterprise": True}},
    {"name": "Analytics", "values": {"free": False, "starter": False, "pro": True, "enterprise": True}},
    {"name": "SSO/SAML", "values": {"free": False, "starter": False, "pro": False, "enterprise": True}},
    {"name": "Priority Support", "values": {"free": False, "starter": False, "pro": True, "enterprise": True}},
    {"name": "SLA", "values": {"free": False, "starter": False, "pro": False, "enterprise": True}},
]


def build_pricing_comparison() -> dict:
    plans = [{"id": p["id"], "name": p["name"],
              "price_display": "Free" if p["price"] == 0 else "Custom" if p["price"] < 0 else f"${p['price']}/mo",
              "recommended": p.get("recommended", False)} for p in PLANS]
    features = []
    for f in FEATURES:
        row = {"name": f["name"], "values": {}}
        for pid in [p["id"] for p in PLANS]:
            val = f["values"].get(pid)
            if isinstance(val, bool):
                row["values"][pid] = {"display": "✓" if val else "✗", "type": "bool", "value": val}
            else:
                row["values"][pid] = {"display": str(val), "type": "text", "value": val}
        features.append(row)
    return {"plans": plans, "features": features, "plan_count": len(plans), "feature_count": len(features)}
