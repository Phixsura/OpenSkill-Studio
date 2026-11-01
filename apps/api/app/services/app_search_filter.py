"""Search filter builder — construct marketplace search filters."""


def build_search_filters(*, query: str | None = None, category: str | None = None,
                          min_health: int | None = None, min_installs: int | None = None,
                          verified_only: bool = False) -> dict:
    filters = {"active": True}
    if query: filters["query"] = query.strip()
    if category: filters["category"] = category
    if min_health is not None: filters["min_health"] = max(0, min(100, min_health))
    if min_installs is not None: filters["min_installs"] = max(0, min_installs)
    if verified_only: filters["verified_only"] = True
    return filters


def apply_filters(apps: list[dict], filters: dict) -> list[dict]:
    results = apps
    if "query" in filters:
        q = filters["query"].lower()
        results = [a for a in results if q in a.get("name", "").lower() or q in a.get("description", "").lower()]
    if "category" in filters:
        results = [a for a in results if a.get("category") == filters["category"]]
    if "min_health" in filters:
        results = [a for a in results if a.get("health_score", 100) >= filters["min_health"]]
    if "min_installs" in filters:
        results = [a for a in results if a.get("install_count", 0) >= filters["min_installs"]]
    if filters.get("verified_only"):
        results = [a for a in results if a.get("developer_verified")]
    return results
