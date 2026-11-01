"""Filter options builder — build available filter options for marketplace."""

def build_filter_options(apps: list[dict]) -> dict:
    categories = sorted(set(a.get("category", "") for a in apps if a.get("category")))
    developers = sorted(set(a.get("developer_name", "") for a in apps if a.get("developer_name")))
    return {"categories": categories, "developers": developers[:20],
            "sort_options": ["relevance", "installs", "newest", "rating", "name"],
            "health_range": {"min": 0, "max": 100}}
