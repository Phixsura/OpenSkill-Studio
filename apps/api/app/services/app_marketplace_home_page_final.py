"""Marketplace home page FINAL — the definitive homepage combining all sections."""


def build_home_page_final(*, user: dict | None, hero: dict, featured: list[dict],
                              trending: list[dict], new_apps: list[dict],
                              categories: list[dict], collections: list[dict],
                              spotlight_devs: list[dict], stats: dict,
                              recommended: list[dict], blog_posts: list[dict]) -> dict:
    sections = []
    if user and recommended:
        sections.append({"key": "recommended", "title": "For You", "type": "carousel", "count": len(recommended)})
    sections.extend([
        {"key": "hero", "type": "hero_banner", "title": hero.get("title", "OpenSkill Marketplace")},
        {"key": "stats", "type": "stats_bar", "apps": stats.get("apps", 0),
         "developers": stats.get("developers", 0), "installs": stats.get("installs", 0)},
        {"key": "featured", "title": "Featured Apps", "type": "carousel", "count": len(featured)},
        {"key": "trending", "title": "Trending This Week", "type": "row", "count": len(trending)},
        {"key": "categories", "title": "Browse Categories", "type": "grid", "count": len(categories)},
        {"key": "spotlight", "title": "Developer Spotlight", "type": "cards", "count": len(spotlight_devs)},
        {"key": "collections", "title": "Collections", "type": "grid", "count": len(collections)},
        {"key": "new", "title": "Just Launched", "type": "row", "count": len(new_apps)},
        {"key": "blog", "title": "From the Blog", "type": "cards", "count": len(blog_posts)},
        {"key": "cta", "type": "cta_section", "title": "Start Building Today"},
    ])
    return {"page_type": "marketplace_home_final", "authenticated": user is not None,
            "sections": sections, "section_count": len(sections)}
