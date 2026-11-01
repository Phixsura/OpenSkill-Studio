"""Developer community — forums, discussions, and Q&A for developers."""

import secrets
from datetime import datetime, timedelta


def create_discussion(*, author_id: str, title: str, body: str,
                        category: str = "general") -> dict:
    if len(title) < 5:
        return {"error": "Title must be at least 5 characters"}
    valid_cats = {"general", "help", "showcase", "feedback", "announcements"}
    if category not in valid_cats:
        return {"error": f"Invalid category. Valid: {', '.join(sorted(valid_cats))}"}
    return {
        "discussion_id": f"disc_{secrets.token_urlsafe(8)}",
        "author_id": author_id,
        "title": title,
        "body": body,
        "category": category,
        "created_at": datetime.utcnow().isoformat(),
        "replies": 0,
        "upvotes": 0,
        "solved": False,
    }


def get_community_stats(*, discussions: list[dict]) -> dict:
    total = len(discussions)
    solved = sum(1 for d in discussions if d.get("solved"))
    by_category: dict[str, int] = {}
    for d in discussions:
        cat = d.get("category", "general")
        by_category[cat] = by_category.get(cat, 0) + 1
    top_contributors: dict[str, int] = {}
    for d in discussions:
        aid = d.get("author_id", "")
        top_contributors[aid] = top_contributors.get(aid, 0) + 1
    top = sorted(top_contributors.items(), key=lambda x: x[1], reverse=True)[:5]
    return {
        "total_discussions": total,
        "solved": solved,
        "solve_rate": round(solved / max(total, 1) * 100, 1),
        "by_category": by_category,
        "top_contributors": [{"user_id": u, "count": c} for u, c in top],
    }
