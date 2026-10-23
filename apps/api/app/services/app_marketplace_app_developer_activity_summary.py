"""Developer activity summary — weekly activity digest for developers."""

from datetime import datetime


def build_weekly_summary(*, developer_name: str, week: str, activity: dict) -> dict:
    commits = activity.get("commits", 0)
    deploys = activity.get("deploys", 0)
    reviews_received = activity.get("reviews_received", 0)
    installs = activity.get("new_installs", 0)
    revenue = activity.get("revenue", 0)
    score = min(commits * 2 + deploys * 10 + reviews_received * 3, 100)
    return {
        "developer_name": developer_name,
        "week": week,
        "activity": {
            "commits": commits,
            "deploys": deploys,
            "reviews_received": reviews_received,
            "new_installs": installs,
            "revenue": round(revenue, 2),
        },
        "activity_score": score,
        "streak_days": activity.get("streak_days", 0),
        "top_achievement": _get_achievement(activity),
    }


def _get_achievement(activity: dict) -> str | None:
    if activity.get("deploys", 0) >= 5:
        return "🚀 Deployment Champion"
    if activity.get("new_installs", 0) >= 100:
        return "📈 Growth Milestone"
    if activity.get("commits", 0) >= 20:
        return "💻 Code Machine"
    if activity.get("streak_days", 0) >= 7:
        return "🔥 7-Day Streak"
    return None
