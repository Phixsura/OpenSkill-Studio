"""Developer rewards — gamification and incentive system for the developer ecosystem."""

REWARD_ACTIONS = {
    "first_app_published": {"points": 100, "badge": "🚀", "title": "First Launch"},
    "10_installs": {"points": 50, "badge": "📈", "title": "Growing"},
    "100_installs": {"points": 200, "badge": "🔥", "title": "On Fire"},
    "5_star_review": {"points": 25, "badge": "⭐", "title": "Star Quality"},
    "security_certified": {"points": 150, "badge": "🔒", "title": "Security Champion"},
    "community_contributor": {"points": 75, "badge": "💬", "title": "Community Hero"},
}


def award_points(*, developer_id: str, action: str) -> dict:
    reward = REWARD_ACTIONS.get(action)
    if not reward:
        return {"error": f"Unknown action: {action}"}
    return {"developer_id": developer_id, "action": action, **reward, "error": None}


def compute_level(*, total_points: int) -> dict:
    levels = [(0, "Beginner", "🌱"), (100, "Explorer", "🧭"), (300, "Builder", "🔨"),
              (600, "Expert", "💎"), (1000, "Master", "👑")]
    level = levels[0]
    for threshold, name, icon in levels:
        if total_points >= threshold:
            level = (threshold, name, icon)
    next_level = None
    for threshold, name, icon in levels:
        if threshold > total_points:
            next_level = {"name": name, "points_needed": threshold - total_points}
            break
    return {"level": level[1], "icon": level[2], "total_points": total_points, "next_level": next_level}


def get_leaderboard(*, developers: list[dict], limit: int = 10) -> list[dict]:
    sorted_devs = sorted(developers, key=lambda d: -d.get("points", 0))
    return [{"rank": i + 1, **d} for i, d in enumerate(sorted_devs[:limit])]
