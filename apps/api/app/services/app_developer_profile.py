"""Developer profile builder — public profile for marketplace."""


def build_public_profile(*, developer: dict, apps: list[dict], stats: dict | None = None) -> dict:
    published = [a for a in apps if a.get("status") == "published"]
    return {
        "display_name": developer.get("display_name"),
        "slug": developer.get("slug"),
        "website_url": developer.get("website_url"),
        "verified": developer.get("verified", False),
        "app_count": len(published),
        "total_installs": sum(a.get("install_count", 0) for a in published),
        "categories": sorted(set(a.get("category", "") for a in published)),
        "apps": [{"id": a["id"], "name": a["name"], "slug": a["slug"], "category": a.get("category"),
                  "install_count": a.get("install_count", 0)} for a in published],
    }
