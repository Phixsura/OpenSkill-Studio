"""Marketplace homepage v3 — the ultimate homepage with all sections and personalization."""


def build_homepage_v3(*, user: dict | None, featured: list[dict], trending: list[dict],
                        new_apps: list[dict], collections: list[dict], categories: list[dict],
                        recommended: list[dict], stats: dict) -> dict:
    sections = []
    # Personalized recommendations first for logged-in users
    if user and recommended:
        sections.append({"key": "recommended", "title": "Recommended for You", "type": "app_grid", "apps": recommended[:8]})
    sections.extend([
        {"key": "hero", "title": "Featured", "type": "hero_carousel", "apps": featured[:6]},
        {"key": "trending", "title": "Trending This Week", "type": "app_row", "apps": trending[:8]},
        {"key": "collections", "title": "Curated Collections", "type": "collection_grid", "data": collections[:4]},
        {"key": "new", "title": "Just Launched", "type": "app_row", "apps": new_apps[:8]},
        {"key": "categories", "title": "Browse Categories", "type": "category_grid", "data": categories},
    ])
    return {
        "page_type": "marketplace_home_v3", "personalized": user is not None,
        "sections": sections, "section_count": len(sections),
        "stats_bar": {"apps": stats.get("total_apps", 0), "developers": stats.get("total_developers", 0),
                        "installs": stats.get("total_installs", 0)},
    }
