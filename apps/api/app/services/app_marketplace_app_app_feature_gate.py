"""Feature gate — plan-based feature gating."""

import html

PLAN_FEATURES = {
    "free": {"max_apps": 5, "max_webhooks": 2, "api_calls_mo": 1000, "custom_domain": False,
             "analytics": False, "priority_support": False, "sso": False},
    "starter": {"max_apps": 25, "max_webhooks": 10, "api_calls_mo": 50000, "custom_domain": True,
                "analytics": False, "priority_support": False, "sso": False},
    "pro": {"max_apps": -1, "max_webhooks": 50, "api_calls_mo": 500000, "custom_domain": True,
            "analytics": True, "priority_support": True, "sso": False},
    "enterprise": {"max_apps": -1, "max_webhooks": -1, "api_calls_mo": -1, "custom_domain": True,
                    "analytics": True, "priority_support": True, "sso": True},
}


def check_feature(*, plan: str, feature: str) -> dict:
    features = PLAN_FEATURES.get(plan, PLAN_FEATURES["free"])
    value = features.get(feature)
    if value is None:
        return {"allowed": False, "error": f"Unknown feature: {feature}"}
    if isinstance(value, bool):
        return {"feature": feature, "allowed": value, "plan": plan,
                "upgrade_needed": not value}
    # Numeric limit: -1 means unlimited
    return {"feature": feature, "allowed": True, "plan": plan,
            "limit": value if value >= 0 else None,
            "unlimited": value < 0}


def get_plan_limits(*, plan: str) -> dict:
    features = PLAN_FEATURES.get(plan, PLAN_FEATURES["free"])
    items = []
    for k, v in features.items():
        if isinstance(v, bool):
            items.append({"feature": k, "type": "boolean", "value": v, "display": "✓" if v else "✗"})
        else:
            items.append({"feature": k, "type": "limit", "value": v,
                          "display": "Unlimited" if v < 0 else f"{v:,}"})
    return {"plan": plan, "features": items, "total": len(items)}
