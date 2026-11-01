"""Complete app page — compile ALL data needed for the marketplace app detail page.

This is the master aggregator that brings together all page builders
into a single API response for the frontend.
"""

from app.services.app_marketplace_app_detail_page_builder import build_detail_page
from app.services.app_marketplace_app_stats_card import build_app_stats_card
from app.services.app_privacy_overview import build_privacy_overview


def build_complete_app_page(*, app: dict, developer: dict, versions: list[dict], stats: dict,
                               health: dict, badges: list[dict], reviews: dict,
                               related: list[dict], permissions: list[str],
                               network_hosts: list[str], secrets_count: int) -> dict:
    """Build the complete app detail page with all sections."""
    detail = build_detail_page(
        app=app, developer=developer, versions=versions, stats=stats,
        health=health, badges=badges, reviews=reviews, related=related,
    )
    stats_card = build_app_stats_card(
        installs=stats.get("installs", 0), executions=stats.get("executions", 0),
        webhooks=stats.get("webhooks", 0), health=health.get("score", 100),
        rating=reviews.get("average", 0), reviews=reviews.get("count", 0),
    )
    privacy = build_privacy_overview(
        permissions=permissions, has_sandbox=bool(app.get("manifest", {}).get("sandbox")),
        network_hosts=network_hosts, secrets_count=secrets_count,
        privacy_url=app.get("privacy_policy_url"),
    )
    
    return {
        **detail,
        "stats_card": stats_card,
        "privacy": privacy,
        "page_type": "app_detail",
        "sections": ["overview", "versions", "permissions", "privacy", "reviews", "related"],
    }
