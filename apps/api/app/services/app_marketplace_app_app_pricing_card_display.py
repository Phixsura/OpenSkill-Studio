"""Pricing card display — format pricing plan for display."""


def build_pricing_card(*, plan: dict, recommended: bool = False) -> dict:
    price = plan.get("price", 0)
    return {
        "id": plan.get("id", ""),
        "name": plan.get("name", ""),
        "price": price,
        "price_display": "Free" if price == 0 else f"${price}" if price > 0 else "Custom",
        "billing": plan.get("billing", "/month"),
        "features": plan.get("features", []),
        "feature_count": len(plan.get("features", [])),
        "cta": plan.get("cta", "Get Started"),
        "recommended": recommended,
        "popular": plan.get("popular", False),
    }
