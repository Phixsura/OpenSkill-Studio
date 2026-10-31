"""Developer reward — gamification rewards for developer engagement."""


REWARDS = [
    {"id": "first_publish", "name": "First Publish", "icon": "🚀", "xp": 100, "trigger": "app_published_count >= 1"},
    {"id": "power_publisher", "name": "Power Publisher", "icon": "📚", "xp": 500, "trigger": "app_published_count >= 10"},
    {"id": "community_hero", "name": "Community Hero", "icon": "🦸", "xp": 300, "trigger": "helpful_reviews >= 50"},
    {"id": "bug_hunter", "name": "Bug Hunter", "icon": "🐛", "xp": 200, "trigger": "bugs_reported >= 10"},
    {"id": "streak_7", "name": "7-Day Streak", "icon": "🔥", "xp": 150, "trigger": "login_streak >= 7"},
    {"id": "revenue_1k", "name": "Revenue Milestone", "icon": "💰", "xp": 1000, "trigger": "revenue >= 1000"},
]


def evaluate_rewards(*, stats: dict) -> dict:
    earned = []
    for reward in REWARDS:
        conditions = {
            "first_publish": stats.get("app_published_count", 0) >= 1,
            "power_publisher": stats.get("app_published_count", 0) >= 10,
            "community_hero": stats.get("helpful_reviews", 0) >= 50,
            "bug_hunter": stats.get("bugs_reported", 0) >= 10,
            "streak_7": stats.get("login_streak", 0) >= 7,
            "revenue_1k": stats.get("revenue", 0) >= 1000,
        }
        if conditions.get(reward["id"], False):
            earned.append(reward)
    total_xp = sum(r["xp"] for r in earned)
    level = total_xp // 500 + 1
    return {
        "earned": earned,
        "earned_count": len(earned),
        "total_available": len(REWARDS),
        "total_xp": total_xp,
        "level": level,
        "next_level_xp": level * 500,
        "xp_to_next": max(level * 500 - total_xp, 0),
    }
