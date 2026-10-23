"""Plan comparison — compare platform plans side by side."""


PLANS = {
    "free": {"price": 0, "apps": 5, "api_calls": 1000, "storage_gb": 1,
             "support": "community", "features": ["basic_analytics"]},
    "starter": {"price": 29, "apps": 25, "api_calls": 50000, "storage_gb": 10,
                "support": "email", "features": ["basic_analytics", "webhooks", "custom_domain"]},
    "pro": {"price": 99, "apps": -1, "api_calls": 500000, "storage_gb": 50,
            "support": "priority", "features": ["advanced_analytics", "webhooks", "custom_domain", "sso", "api_playground"]},
    "enterprise": {"price": -1, "apps": -1, "api_calls": -1, "storage_gb": -1,
                   "support": "dedicated", "features": ["advanced_analytics", "webhooks", "custom_domain", "sso", "api_playground", "sla", "audit_log"]},
}


def compare_plans(*, plan_ids: list[str] | None = None) -> dict:
    ids = plan_ids or list(PLANS.keys())
    plans = []
    all_features = set()
    for pid in ids:
        p = PLANS.get(pid)
        if p:
            all_features.update(p["features"])
            plans.append({"id": pid, **p,
                          "apps_label": "Unlimited" if p["apps"] == -1 else str(p["apps"]),
                          "api_label": "Unlimited" if p["api_calls"] == -1 else f"{p['api_calls']:,}",
                          "price_label": "Custom" if p["price"] == -1 else f"${p['price']}/mo" if p["price"] > 0 else "Free"})
    feature_matrix = []
    for feat in sorted(all_features):
        row = {"feature": feat}
        for plan in plans:
            row[plan["id"]] = feat in plan["features"]
        feature_matrix.append(row)
    return {"plans": plans, "feature_matrix": feature_matrix,
            "total_plans": len(plans), "total_features": len(all_features)}
