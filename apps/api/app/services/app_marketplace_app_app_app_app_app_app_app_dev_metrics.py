"""Developer metrics summary — per-developer performance overview."""
from __future__ import annotations


def compute_dev_metrics(*, developer_id: str, apps: list[dict],
                          support_tickets: int = 0, avg_response_hours: float = 0) -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    total_reviews = sum(a.get("reviews", 0) for a in apps)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1)
    total_api_calls = sum(a.get("api_calls", 0) for a in apps)
    return {
        "developer_id": developer_id,
        "app_count": len(apps),
        "total_installs": total_installs, "installs_display": f"{total_installs:,}",
        "total_reviews": total_reviews,
        "avg_rating": avg_rating, "rating_display": f"{avg_rating} ⭐",
        "total_api_calls": total_api_calls, "api_display": f"{total_api_calls:,}",
        "support_tickets": support_tickets,
        "avg_response_hours": avg_response_hours,
        "support_grade": "A" if avg_response_hours < 4 else "B" if avg_response_hours < 12 else "C",
        "quality_score": _quality(avg_rating, total_reviews, avg_response_hours),
    }


def _quality(rating: float, reviews: int, response_h: float) -> int:
    score = int(rating * 15)
    if reviews > 100:
        score += 15
    elif reviews > 10:
        score += 5
    if response_h < 4:
        score += 10
    return min(100, score)
