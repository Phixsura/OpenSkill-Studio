"""Complete developer app list — the main apps page in the developer portal."""


def build_developer_app_list(*, apps: list[dict], sort_by: str = "recent",
                                  filter_status: str | None = None) -> dict:
    filtered = apps
    if filter_status:
        filtered = [a for a in filtered if a.get("status") == filter_status]
    if sort_by == "recent":
        filtered = sorted(filtered, key=lambda a: a.get("updated_at", ""), reverse=True)
    elif sort_by == "installs":
        filtered = sorted(filtered, key=lambda a: -a.get("install_count", 0))
    elif sort_by == "name":
        filtered = sorted(filtered, key=lambda a: a.get("name", "").lower())
    # Stats
    published = sum(1 for a in apps if a.get("status") == "published")
    draft = sum(1 for a in apps if a.get("status") == "draft")
    in_review = sum(1 for a in apps if a.get("status") == "in_review")
    return {
        "page_type": "developer_app_list",
        "apps": filtered,
        "stats": {"total": len(apps), "published": published, "draft": draft, "in_review": in_review},
        "sort_by": sort_by,
        "filter_status": filter_status,
        "filter_options": ["all", "published", "draft", "in_review", "archived"],
        "sort_options": ["recent", "installs", "name"],
    }
