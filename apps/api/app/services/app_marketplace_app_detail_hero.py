"""App detail hero — the hero section at the top of app detail pages."""


def build_app_detail_hero(*, app: dict, developer: dict, stats: dict,
                             badges: list[dict], installed: bool = False) -> dict:
    return {
        "app": {"name": app["name"], "slug": app.get("slug"), "icon": app.get("icon"),
                "short_description": app.get("short_description", app.get("description", ""))[:200],
                "category": app.get("category"), "price_label": app.get("price_label", "Free")},
        "developer": {"name": developer.get("display_name"), "slug": developer.get("slug"),
                        "verified": developer.get("verified", False)},
        "stats": {"installs": stats.get("install_count", 0), "rating": stats.get("avg_rating", 0),
                   "reviews": stats.get("review_count", 0), "version": app.get("current_version")},
        "badges": badges[:5],
        "cta": {"label": "Installed" if installed else "Install",
                "action": "manage" if installed else "install",
                "disabled": installed},
    }
