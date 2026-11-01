"""Cost breakdown — detailed cost analysis by resource and service."""


def calculate_cost_breakdown(*, resources: list[dict]) -> dict:
    line_items = []
    total = 0.0
    by_category: dict[str, float] = {}
    for r in resources:
        cost = round(r.get("quantity", 0) * r.get("unit_price", 0), 2)
        cat = r.get("category", "other")
        by_category[cat] = round(by_category.get(cat, 0) + cost, 2)
        line_items.append({
            "name": r["name"],
            "category": cat,
            "quantity": r.get("quantity", 0),
            "unit": r.get("unit", "units"),
            "unit_price": r.get("unit_price", 0),
            "total": cost,
        })
        total += cost
    sorted_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    return {
        "line_items": line_items,
        "total": round(total, 2),
        "by_category": dict(sorted_cats),
        "largest_category": sorted_cats[0][0] if sorted_cats else None,
        "item_count": len(line_items),
    }
