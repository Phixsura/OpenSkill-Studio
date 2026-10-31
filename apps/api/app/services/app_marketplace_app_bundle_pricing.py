"""Bundle pricing — create and price app bundles with discounts."""


def create_bundle(*, name: str, apps: list[dict], discount_pct: float = 20.0) -> dict:
    if len(apps) < 2:
        return {"error": "Bundle requires at least 2 apps"}
    if not 0 <= discount_pct <= 50:
        return {"error": "Discount must be 0-50%"}
    individual_total = sum(a.get("price", 0) for a in apps)
    bundle_price = round(individual_total * (1 - discount_pct / 100), 2)
    savings = round(individual_total - bundle_price, 2)
    return {
        "name": name,
        "apps": [{"id": a["id"], "name": a["name"], "price": a.get("price", 0)} for a in apps],
        "app_count": len(apps),
        "individual_total": individual_total,
        "bundle_price": bundle_price,
        "savings": savings,
        "discount_pct": discount_pct,
    }


def calculate_tier_pricing(*, base_price: float, tiers: list[dict]) -> dict:
    results = []
    for t in tiers:
        multiplier = t.get("multiplier", 1.0)
        price = round(base_price * multiplier, 2)
        results.append({"tier": t["name"], "price": price,
                         "features": t.get("features", []),
                         "recommended": t.get("recommended", False)})
    return {"base_price": base_price, "tiers": results}
