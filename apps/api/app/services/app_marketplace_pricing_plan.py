"""Pricing plans — manage free/paid tiers for marketplace apps."""

VALID_INTERVALS = {"monthly", "yearly", "one_time"}


def create_pricing_plan(*, app_id: str, name: str, price_cents: int,
                          interval: str, features: list[str]) -> dict:
    if interval not in VALID_INTERVALS:
        return {"error": f"Invalid interval. Use: {', '.join(sorted(VALID_INTERVALS))}"}
    if price_cents < 0:
        return {"error": "Price cannot be negative"}
    return {
        "app_id": app_id, "name": name, "price_cents": price_cents,
        "interval": interval, "features": features,
        "is_free": price_cents == 0, "status": "active", "error": None,
    }


def compare_plans(*, plans: list[dict]) -> dict:
    all_features = set()
    for p in plans:
        all_features.update(p.get("features", []))
    matrix = []
    for feat in sorted(all_features):
        row = {"feature": feat}
        for p in plans:
            row[p["name"]] = feat in p.get("features", [])
        matrix.append(row)
    return {"plans": [{"name": p["name"], "price_cents": p["price_cents"]} for p in plans],
            "matrix": matrix}


def calculate_savings(*, monthly_price: int, yearly_price: int) -> dict:
    annual_monthly = monthly_price * 12
    if annual_monthly == 0:
        return {"savings_pct": 0, "savings_cents": 0}
    savings = annual_monthly - yearly_price
    return {"savings_pct": round(savings / annual_monthly * 100), "savings_cents": savings}
