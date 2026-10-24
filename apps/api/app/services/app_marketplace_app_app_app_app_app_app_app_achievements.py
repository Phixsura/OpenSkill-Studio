"""Developer achievement badges — gamification for platform milestones."""
from __future__ import annotations

ACHIEVEMENTS = {
    "first_app": {"title": "App Creator", "icon": "📱", "description": "Created your first app", "points": 10},
    "first_deploy": {"title": "Deployer", "icon": "🚀", "description": "Made your first deployment", "points": 15},
    "hundred_users": {"title": "Popular", "icon": "👥", "description": "Reached 100 users", "points": 25},
    "five_star": {"title": "Five Star", "icon": "⭐", "description": "Received a 5-star review", "points": 20},
    "api_million": {"title": "Million Calls", "icon": "📡", "description": "1M API calls processed", "points": 50},
    "contributor": {"title": "Contributor", "icon": "🤝", "description": "Contributed to community", "points": 30},
    "bug_hunter": {"title": "Bug Hunter", "icon": "🐛", "description": "Reported 10 bugs", "points": 20},
    "speed_demon": {"title": "Speed Demon", "icon": "⚡", "description": "Sub-100ms avg response", "points": 35},
}


def check_achievements(user_stats: dict) -> list[dict]:
    earned = []
    if user_stats.get("apps", 0) >= 1:
        earned.append(ACHIEVEMENTS["first_app"])
    if user_stats.get("deploys", 0) >= 1:
        earned.append(ACHIEVEMENTS["first_deploy"])
    if user_stats.get("users", 0) >= 100:
        earned.append(ACHIEVEMENTS["hundred_users"])
    if user_stats.get("five_star_reviews", 0) >= 1:
        earned.append(ACHIEVEMENTS["five_star"])
    if user_stats.get("api_calls", 0) >= 1000000:
        earned.append(ACHIEVEMENTS["api_million"])
    if user_stats.get("avg_response_ms", 999) < 100:
        earned.append(ACHIEVEMENTS["speed_demon"])
    return earned


def compute_level(points: int) -> dict:
    if points >= 200:
        return {"level": 5, "title": "Platform Master", "next_at": None}
    if points >= 100:
        return {"level": 4, "title": "Expert", "next_at": 200}
    if points >= 50:
        return {"level": 3, "title": "Builder", "next_at": 100}
    if points >= 20:
        return {"level": 2, "title": "Explorer", "next_at": 50}
    return {"level": 1, "title": "Newcomer", "next_at": 20}
