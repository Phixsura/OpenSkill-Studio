"""Rate plan configurator — define tiered pricing plans with feature gates."""
from __future__ import annotations

PLANS = {
    "free": {"price": 0, "api_calls": 1000, "apps": 3, "team_size": 1,
             "features": ["basic_analytics", "community_support"]},
    "starter": {"price": 29, "api_calls": 50000, "apps": 10, "team_size": 5,
                 "features": ["basic_analytics", "email_support", "webhooks", "custom_domain"]},
    "pro": {"price": 99, "api_calls": 500000, "apps": 50, "team_size": 25,
             "features": ["advanced_analytics", "priority_support", "webhooks", "custom_domain", "sso", "audit_logs"]},
    "enterprise": {"price": -1, "api_calls": -1, "apps": -1, "team_size": -1,
                    "features": ["advanced_analytics", "dedicated_support", "webhooks", "custom_domain", "sso", "audit_logs", "sla", "custom_contracts"]},
}


def get_plan(plan_id: str) -> dict:
    plan = PLANS.get(plan_id)
    if not plan:
        return {"error": f"Unknown plan: {plan_id}"}
    return {"id": plan_id, **plan,
            "price_display": "Custom" if plan["price"] == -1 else f"${plan['price']}/mo",
            "is_unlimited": plan["api_calls"] == -1}


def compare_plans() -> list[dict]:
    all_features = sorted({f for p in PLANS.values() for f in p["features"]})
    result = []
    for pid, plan in PLANS.items():
        row = {"id": pid, "price_display": "Custom" if plan["price"] == -1 else f"${plan['price']}/mo"}
        for feat in all_features:
            row[feat] = feat in plan["features"]
        result.append(row)
    return result


def can_use_feature(plan_id: str, feature: str) -> bool:
    plan = PLANS.get(plan_id, {})
    return feature in plan.get("features", [])
