"""Developer profile — public developer profile and portfolio."""

import html


def build_developer_profile(*, developer: dict, apps: list[dict]) -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1)
    top_apps = sorted(apps, key=lambda a: a.get("installs", 0), reverse=True)[:5]
    categories = list(set(a.get("category", "other") for a in apps))
    return {
        "developer_id": developer.get("id"),
        "display_name": html.escape(developer.get("display_name", "")),
        "bio": html.escape(developer.get("bio", "")),
        "avatar": developer.get("avatar"),
        "website": developer.get("website"),
        "joined": developer.get("joined"),
        "stats": {
            "total_apps": len(apps),
            "total_installs": total_installs,
            "avg_rating": avg_rating,
            "categories": sorted(categories),
        },
        "top_apps": [{"id": a["id"], "name": a["name"],
                       "installs": a.get("installs", 0)} for a in top_apps],
        "verified": developer.get("verified", False),
    }
