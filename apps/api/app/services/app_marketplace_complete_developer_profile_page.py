"""Complete developer profile page — public profile with apps, stats, and badges."""


def build_complete_developer_profile_page(*, developer: dict, apps: list[dict],
                                               badges: list[dict], achievements: list[dict],
                                               stats: dict, reviews_summary: dict) -> dict:
    published = [a for a in apps if a.get("status") == "published"]
    total_installs = sum(a.get("install_count", 0) for a in published)
    return {
        "page_type": "developer_profile",
        "hero": {
            "name": developer.get("display_name"), "slug": developer.get("slug"),
            "bio": developer.get("bio", ""), "avatar": developer.get("avatar"),
            "verified": developer.get("verified", False),
            "joined": developer.get("created_at", "")[:10],
            "website": developer.get("website"),
        },
        "stats": {
            "published_apps": len(published), "total_installs": total_installs,
            "avg_rating": reviews_summary.get("avg_rating", 0),
            "total_reviews": reviews_summary.get("total_reviews", 0),
        },
        "apps": [{"id": a["id"], "name": a["name"], "slug": a.get("slug"),
                   "category": a.get("category"), "install_count": a.get("install_count", 0),
                   "avg_rating": a.get("avg_rating", 0)} for a in published],
        "badges": badges[:10],
        "achievements": achievements[:8],
        "seo": {"title": f"{developer.get('display_name', '')} — OpenSkill Developer",
                "description": developer.get("bio", "")[:160]},
    }
