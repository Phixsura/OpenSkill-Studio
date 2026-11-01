"""Search filters — comprehensive filter system for marketplace search."""

from collections import defaultdict


FILTER_DEFINITIONS = {
    "category": {"label": "Category", "type": "select", "options": ["connector", "automation", "analytics", "communication", "developer_tools", "security"]},
    "rating": {"label": "Minimum Rating", "type": "range", "min": 1, "max": 5, "step": 0.5},
    "pricing": {"label": "Pricing", "type": "select", "options": ["free", "freemium", "paid"]},
    "sort": {"label": "Sort By", "type": "select", "options": ["relevance", "rating", "installs", "newest", "name"]},
    "verified_developer": {"label": "Verified Developer", "type": "boolean"},
    "has_free_trial": {"label": "Free Trial", "type": "boolean"},
}


def get_filter_definitions() -> dict:
    return FILTER_DEFINITIONS


def apply_filters(*, apps: list[dict], filters: dict) -> list[dict]:
    result = list(apps)
    if filters.get("category"):
        result = [a for a in result if a.get("category") == filters["category"]]
    if filters.get("rating"):
        min_rating = float(filters["rating"])
        result = [a for a in result if a.get("avg_rating", 0) >= min_rating]
    if filters.get("pricing"):
        if filters["pricing"] == "free":
            result = [a for a in result if a.get("price_cents", 0) == 0]
        elif filters["pricing"] == "paid":
            result = [a for a in result if a.get("price_cents", 0) > 0]
    if filters.get("verified_developer"):
        result = [a for a in result if a.get("developer_verified")]
    if filters.get("has_free_trial"):
        result = [a for a in result if a.get("has_free_trial")]
    # Sort
    sort_key = filters.get("sort", "relevance")
    if sort_key == "rating":
        result.sort(key=lambda a: -a.get("avg_rating", 0))
    elif sort_key == "installs":
        result.sort(key=lambda a: -a.get("install_count", 0))
    elif sort_key == "newest":
        result.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    elif sort_key == "name":
        result.sort(key=lambda a: a.get("name", "").lower())
    return result


def compute_filter_counts(*, apps: list[dict]) -> dict:
    counts = defaultdict(lambda: defaultdict(int))
    for a in apps:
        if a.get("category"):
            counts["category"][a["category"]] += 1
        if a.get("price_cents", 0) == 0:
            counts["pricing"]["free"] += 1
        else:
            counts["pricing"]["paid"] += 1
        if a.get("developer_verified"):
            counts["verified"]["yes"] += 1
    return {k: dict(v) for k, v in counts.items()}
