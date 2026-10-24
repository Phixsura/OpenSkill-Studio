"""Marketplace stats summary — aggregate marketplace-wide statistics."""
from __future__ import annotations


def compute_marketplace_stats(*, total_apps: int, total_developers: int,
                                 total_installs: int, total_api_calls: int,
                                 avg_rating: float, total_reviews: int,
                                 categories: int, new_apps_30d: int) -> dict:
    return {
        "total_apps": total_apps, "apps_display": f"{total_apps:,}",
        "total_developers": total_developers, "devs_display": f"{total_developers:,}",
        "total_installs": total_installs, "installs_display": f"{total_installs:,}",
        "total_api_calls": total_api_calls, "api_display": f"{total_api_calls:,}",
        "avg_rating": avg_rating, "rating_display": f"{avg_rating} ⭐",
        "total_reviews": total_reviews, "reviews_display": f"{total_reviews:,}",
        "categories": categories,
        "new_apps_30d": new_apps_30d,
        "growth_display": f"+{new_apps_30d} this month",
        "health": "thriving" if new_apps_30d > 20 else "growing" if new_apps_30d > 5 else "stable",
    }
