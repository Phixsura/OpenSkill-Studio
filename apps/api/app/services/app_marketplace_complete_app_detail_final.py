"""Complete app detail FINAL — the definitive app detail page aggregator.

Combines hero, tabs (overview, reviews, changelog, docs, support), sidebar,
and all related data into one comprehensive response.
"""


def build_app_detail_final(*, app: dict, developer: dict, current_version: dict | None,
                               reviews: dict, install_stats: dict, screenshots: list[dict],
                               changelog: list[dict], related: list[dict], pricing: dict | None,
                               badges: list[dict], installed: bool, wishlisted: bool) -> dict:
    return {
        "page_type": "app_detail_final",
        "hero": {
            "name": app["name"], "slug": app.get("slug"), "icon": app.get("icon"),
            "description": app.get("description", ""), "category": app.get("category"),
            "developer": {"name": developer.get("display_name"), "verified": developer.get("verified", False)},
            "badges": badges[:5],
            "cta": {"label": "Installed ✓" if installed else "Install", "disabled": installed},
            "wishlist": {"active": wishlisted},
        },
        "tabs": [
            {"key": "overview", "title": "Overview"},
            {"key": "reviews", "title": f"Reviews ({reviews.get('count', 0)})"},
            {"key": "changelog", "title": f"Changelog ({len(changelog)})"},
            {"key": "docs", "title": "Documentation"},
            {"key": "support", "title": "Support"},
        ] + ([{"key": "pricing", "title": "Pricing"}] if pricing else []),
        "sidebar": {
            "version": current_version, "install_stats": install_stats,
            "screenshots": screenshots[:6], "related": related[:4],
        },
        "reviews_summary": reviews,
        "seo": {"title": f"{app['name']} — OpenSkill Marketplace",
                "description": app.get("description", "")[:160]},
    }
