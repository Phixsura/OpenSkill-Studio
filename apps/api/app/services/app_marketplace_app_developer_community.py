"""Developer community — forums, discussions, and Q&A for app developers."""

from datetime import datetime, timezone


def create_discussion(*, author_id: str, app_id: str | None, title: str, body: str,
                        category: str = "general") -> dict:
    valid_categories = {"general", "help", "showcase", "feedback", "announcement"}
    if category not in valid_categories:
        return {"error": f"Invalid category. Use: {', '.join(sorted(valid_categories))}"}
    return {"author_id": author_id, "app_id": app_id, "title": title, "body": body,
            "category": category, "replies": 0, "upvotes": 0,
            "created_at": datetime.now(timezone.utc).isoformat(), "error": None}


def get_trending_discussions(*, discussions: list[dict], limit: int = 10) -> list[dict]:
    scored = []
    for d in discussions:
        score = d.get("upvotes", 0) * 2 + d.get("replies", 0) * 3
        scored.append({**d, "trending_score": score})
    return sorted(scored, key=lambda x: -x["trending_score"])[:limit]


def get_community_stats(*, discussions: list[dict], members: int) -> dict:
    total_replies = sum(d.get("replies", 0) for d in discussions)
    return {"total_discussions": len(discussions), "total_replies": total_replies,
            "members": members, "avg_replies": round(total_replies / max(len(discussions), 1), 1)}
