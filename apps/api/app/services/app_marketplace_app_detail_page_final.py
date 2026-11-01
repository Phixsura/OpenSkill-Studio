"""App detail page FINAL — the absolute last app detail page aggregator combining every element."""


def build_app_detail_page_final(*, app: dict, developer: dict, version: dict | None,
                                     reviews: dict, stats: dict, screenshots: list[str],
                                     changelog: list[dict], related: list[dict],
                                     badges: list[dict], pricing: dict | None,
                                     installed: bool, wishlisted: bool,
                                     support: dict, faq: list[dict]) -> dict:
    tabs = [
        {"key": "overview", "title": "Overview", "default": True},
        {"key": "reviews", "title": f"Reviews ({reviews.get('count', 0)})"},
        {"key": "changelog", "title": f"Changelog ({len(changelog)})"},
        {"key": "support", "title": "Support"},
    ]
    if pricing:
        tabs.insert(3, {"key": "pricing", "title": "Pricing"})

    return {
        "page_type": "app_detail_page_final",
        "hero": {
            "app": {"name": app["name"], "slug": app.get("slug"), "icon": app.get("icon"),
                     "short_desc": app.get("description", "")[:200], "category": app.get("category"),
                     "price_label": app.get("price_label", "Free")},
            "developer": {"name": developer.get("display_name"), "slug": developer.get("slug"),
                            "verified": developer.get("verified", False)},
            "badges": badges[:5],
            "cta": {"installed": installed, "wishlisted": wishlisted},
        },
        "tabs": tabs,
        "sidebar": {
            "version": version, "stats": stats, "screenshots": screenshots[:6],
            "related": related[:4], "support_email": support.get("email"),
        },
        "seo": {"title": f"{app['name']} — OpenSkill Marketplace",
                "description": app.get("description", "")[:160]},
    }
