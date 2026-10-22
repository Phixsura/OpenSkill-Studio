"""Complete developer page — compile all data for developer public profile."""

from app.services.app_developer_profile import build_public_profile


def build_complete_developer_page(*, developer: dict, apps: list[dict], stats: dict,
                                     recent_versions: list[dict]) -> dict:
    profile = build_public_profile(developer=developer, apps=apps, stats=stats)
    return {
        **profile,
        "recent_versions": recent_versions[:5],
        "page_type": "developer_profile",
        "tabs": ["apps", "changelog", "about"],
        "seo": {
            "title": f"{developer.get('display_name', '')} | OpenSkill Developer",
            "description": f"Apps by {developer.get('display_name', '')} on OpenSkill Marketplace",
        },
    }
