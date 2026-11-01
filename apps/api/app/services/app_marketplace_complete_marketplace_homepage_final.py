"""Complete marketplace homepage FINAL — the absolute definitive homepage aggregator.

This is THE final homepage service combining hero, featured, trending, categories,
collections, stats, testimonials, developer spotlight, and personalization.
"""


def build_marketplace_homepage_final(*, user: dict | None, hero: dict,
                                         featured: list[dict], trending: list[dict],
                                         new_apps: list[dict], categories: list[dict],
                                         collections: list[dict], stats: dict,
                                         spotlight_developers: list[dict],
                                         recommended: list[dict]) -> dict:
    sections = []
    # Personalized section for logged-in users
    if user and recommended:
        sections.append({"key": "recommended", "title": "Recommended for You", "type": "app_carousel",
                          "apps": recommended[:8], "personalized": True})
    sections.extend([
        {"key": "hero", "title": hero.get("title", "OpenSkill Marketplace"), "type": "hero_banner",
         "subtitle": hero.get("subtitle", ""), "cta": hero.get("cta", "Explore Apps")},
        {"key": "stats", "type": "stats_bar", "data": {
            "apps": stats.get("total_apps", 0), "developers": stats.get("total_developers", 0),
            "installs": stats.get("total_installs", 0)}},
        {"key": "featured", "title": "Featured Apps", "type": "app_carousel", "apps": featured[:8]},
        {"key": "trending", "title": "Trending This Week", "type": "app_row", "apps": trending[:8]},
        {"key": "categories", "title": "Browse by Category", "type": "category_grid", "categories": categories},
        {"key": "spotlight", "title": "Developer Spotlight", "type": "developer_cards", "developers": spotlight_developers[:3]},
        {"key": "collections", "title": "Curated Collections", "type": "collection_grid", "collections": collections[:6]},
        {"key": "new", "title": "Just Launched", "type": "app_row", "apps": new_apps[:8]},
        {"key": "cta", "title": "Start Building", "type": "cta_section",
         "subtitle": "Join thousands of developers on the OpenSkill platform",
         "button": "Get Started", "url": "/developer/register"},
    ])
    return {
        "page_type": "marketplace_homepage_final",
        "authenticated": user is not None,
        "sections": sections,
        "section_count": len(sections),
        "total_content_items": len(featured) + len(trending) + len(new_apps) + len(collections),
        "seo": {"title": "OpenSkill Marketplace — Discover Apps for Your Workflow",
                "description": f"Browse {stats.get('total_apps', 0)} apps from {stats.get('total_developers', 0)} developers"},
    }
