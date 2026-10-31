"""Developer achievements — track milestones and unlock achievements."""

ACHIEVEMENTS = [
    {"id": "first_app", "title": "Hello World", "desc": "Publish your first app", "icon": "🌍", "points": 50},
    {"id": "popular_10", "title": "Rising Star", "desc": "Get 10 installations", "icon": "⭐", "points": 100},
    {"id": "popular_100", "title": "Hit Maker", "desc": "Get 100 installations", "icon": "🔥", "points": 250},
    {"id": "five_stars", "title": "Perfectionist", "desc": "Receive a 5-star review", "icon": "💎", "points": 75},
    {"id": "multi_app", "title": "Portfolio Builder", "desc": "Publish 3 apps", "icon": "📦", "points": 150},
    {"id": "zero_downtime", "title": "Iron Uptime", "desc": "99.99% uptime for 30 days", "icon": "🛡️", "points": 200},
    {"id": "community_hero", "title": "Community Hero", "desc": "Answer 10 questions", "icon": "💬", "points": 100},
    {"id": "speed_demon", "title": "Speed Demon", "desc": "Sub-100ms average response", "icon": "⚡", "points": 150},
]

def check_achievements(*, stats: dict) -> list[dict]:
    unlocked = []
    if stats.get("apps_published", 0) >= 1:
        unlocked.append("first_app")
    if stats.get("total_installs", 0) >= 10:
        unlocked.append("popular_10")
    if stats.get("total_installs", 0) >= 100:
        unlocked.append("popular_100")
    if stats.get("has_five_star"):
        unlocked.append("five_stars")
    if stats.get("apps_published", 0) >= 3:
        unlocked.append("multi_app")
    return [a for a in ACHIEVEMENTS if a["id"] in unlocked]

def get_achievement_progress(*, stats: dict) -> list[dict]:
    progress = []
    for a in ACHIEVEMENTS:
        earned = a["id"] in [x["id"] for x in check_achievements(stats=stats)]
        progress.append({**a, "earned": earned})
    return progress
