"""Marketplace homepage v2 — personalized homepage based on user preferences."""


def build_homepage_v2(*, user: dict | None, featured: list[dict], trending: list[dict],
                        recommended: list[dict], new_apps: list[dict], collections: list[dict]) -> dict:
    sections = [{"key": "featured", "title": "Featured", "apps": featured[:6]}]
    if user and recommended:
        sections.insert(0, {"key": "recommended", "title": "Recommended for You", "apps": recommended[:6]})
    sections.extend([
        {"key": "trending", "title": "Trending This Week", "apps": trending[:8]},
        {"key": "new", "title": "Just Launched", "apps": new_apps[:8]},
        {"key": "collections", "title": "Collections", "data": collections[:4]},
    ])
    return {"page_type": "marketplace_home_v2", "personalized": user is not None,
            "sections": sections, "section_count": len(sections)}
