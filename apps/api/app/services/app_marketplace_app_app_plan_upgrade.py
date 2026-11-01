"""Plan upgrade — plan upgrade/downgrade flow."""

import html

PLANS = {
    "free": {"price": 0, "order": 0},
    "starter": {"price": 9, "order": 1},
    "pro": {"price": 29, "order": 2},
    "enterprise": {"price": 99, "order": 3},
}


def build_upgrade_flow(*, current_plan: str, target_plan: str) -> dict:
    current = PLANS.get(current_plan, PLANS["free"])
    target = PLANS.get(target_plan, PLANS["free"])
    is_upgrade = target["order"] > current["order"]
    price_diff = target["price"] - current["price"]
    return {
        "current_plan": current_plan, "target_plan": target_plan,
        "is_upgrade": is_upgrade, "is_downgrade": not is_upgrade and target_plan != current_plan,
        "price_diff": price_diff, "price_diff_display": f"+${price_diff}/mo" if price_diff > 0 else f"-${abs(price_diff)}/mo" if price_diff < 0 else "$0",
        "new_price": target["price"],
        "requires_payment": target["price"] > 0 and is_upgrade,
        "warning": "Some features will be disabled" if not is_upgrade and target_plan != current_plan else None,
    }
