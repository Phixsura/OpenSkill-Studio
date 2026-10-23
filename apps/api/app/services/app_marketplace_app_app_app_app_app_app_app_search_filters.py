"""Search filter builder — composable filters for marketplace search."""
from __future__ import annotations


def build_filters(*, categories: list[str] | None = None,
                    rating_min: float = 0, price_type: str | None = None,
                    sort_by: str = "relevance", verified_only: bool = False) -> dict:
    active = []
    if categories:
        active.append({"key": "categories", "values": categories, "display": ", ".join(categories)})
    if rating_min > 0:
        active.append({"key": "rating_min", "values": [rating_min], "display": f"≥ {rating_min}⭐"})
    if price_type:
        active.append({"key": "price_type", "values": [price_type], "display": price_type.capitalize()})
    if verified_only:
        active.append({"key": "verified", "values": [True], "display": "Verified ✓"})
    return {"filters": active, "active_count": len(active), "sort_by": sort_by,
            "has_filters": len(active) > 0}


def apply_filters(apps: list[dict], filters: dict) -> list[dict]:
    result = list(apps)
    for f in filters.get("filters", []):
        if f["key"] == "categories":
            result = [a for a in result if a.get("category") in f["values"]]
        elif f["key"] == "rating_min":
            result = [a for a in result if a.get("rating", 0) >= f["values"][0]]
        elif f["key"] == "price_type":
            result = [a for a in result if a.get("price_type") == f["values"][0]]
        elif f["key"] == "verified":
            result = [a for a in result if a.get("verified", False)]
    sort = filters.get("sort_by", "relevance")
    if sort == "rating":
        result.sort(key=lambda a: -a.get("rating", 0))
    elif sort == "installs":
        result.sort(key=lambda a: -a.get("installs", 0))
    return result
