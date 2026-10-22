"""Marketplace statistics — compute marketplace-level aggregate stats."""


def compute_marketplace_stats(
    *,
    total_apps: int = 0,
    published_apps: int = 0,
    total_developers: int = 0,
    total_installations: int = 0,
    apps_by_category: dict[str, int] | None = None,
) -> dict:
    """Compute marketplace overview statistics."""
    categories = apps_by_category or {}
    return {
        "total_apps": total_apps,
        "published_apps": published_apps,
        "total_developers": total_developers,
        "total_installations": total_installations,
        "apps_by_category": categories,
        "top_categories": sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5],
        "avg_installs_per_app": round(total_installations / published_apps, 1) if published_apps > 0 else 0,
    }
