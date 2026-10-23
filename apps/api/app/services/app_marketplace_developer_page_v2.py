"""Developer page v2 — public developer profile with apps, badges, and stats."""


def build_developer_page_v2(*, developer: dict, apps: list[dict], badges: list[dict],
                                reviews_summary: dict, achievements: list[dict]) -> dict:
    published = [a for a in apps if a.get("status") == "published"]
    total_installs = sum(a.get("install_count", 0) for a in apps)
    return {
        "page_type": "developer_profile_v2",
        "developer": {
            "name": developer.get("display_name"), "slug": developer.get("slug"),
            "bio": developer.get("bio", ""), "avatar": developer.get("avatar"),
            "verified": developer.get("verified", False), "joined_at": developer.get("created_at"),
        },
        "stats": {"total_apps": len(apps), "published_apps": len(published),
                   "total_installs": total_installs, "avg_rating": reviews_summary.get("avg_rating", 0)},
        "apps": [{"id": a["id"], "name": a["name"], "category": a.get("category"),
                   "installs": a.get("install_count", 0)} for a in published],
        "badges": badges, "achievements": achievements[:10],
        "seo": {"title": f"{developer.get('display_name', '')} | OpenSkill Developer",
                "description": developer.get("bio", "")[:160]},
    }
