"""Review reply — developers can respond to user reviews."""

from datetime import datetime, timezone


def create_reply(*, review_id: str, developer_id: str, body: str) -> dict:
    if len(body) < 10:
        return {"error": "Reply must be at least 10 characters"}
    if len(body) > 2000:
        return {"error": "Reply must be under 2000 characters"}
    return {"review_id": review_id, "developer_id": developer_id, "body": body,
            "created_at": datetime.now(timezone.utc).isoformat(), "error": None}


def get_reply_stats(*, reviews: list[dict]) -> dict:
    total = len(reviews)
    replied = sum(1 for r in reviews if r.get("has_reply"))
    return {"total_reviews": total, "replied": replied, "unreplied": total - replied,
            "reply_rate": round(replied / max(total, 1) * 100, 1)}


def get_unreplied_reviews(*, reviews: list[dict], sort_by: str = "oldest") -> list[dict]:
    unreplied = [r for r in reviews if not r.get("has_reply")]
    if sort_by == "oldest":
        return sorted(unreplied, key=lambda r: r.get("created_at", ""))
    elif sort_by == "lowest_rating":
        return sorted(unreplied, key=lambda r: r.get("rating", 5))
    return unreplied
