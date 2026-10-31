"""Marketplace listing optimizer — A/B test and optimize listing elements."""


def create_listing_experiment(*, app_id: str, element: str, variants: list[str]) -> dict:
    valid_elements = {"title", "description", "icon", "screenshots", "tags"}
    if element not in valid_elements:
        return {"error": f"Invalid element. Use: {', '.join(sorted(valid_elements))}"}
    if len(variants) < 2:
        return {"error": "Need at least 2 variants"}
    return {"app_id": app_id, "element": element, "variants": variants,
            "variant_count": len(variants), "status": "draft", "error": None}


def evaluate_listing_experiment(*, variants_data: list[dict]) -> dict:
    best = max(variants_data, key=lambda v: v.get("conversion_rate", 0))
    return {"winner": best.get("variant"), "best_rate": best.get("conversion_rate", 0),
            "variants": variants_data, "significant": len(variants_data) >= 2 and
            all(v.get("impressions", 0) >= 100 for v in variants_data)}
