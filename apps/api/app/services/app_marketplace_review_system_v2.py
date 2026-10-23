"""Review system v2 — structured reviews with pros/cons, verified purchases, and moderation."""


def create_review_v2(*, app_id: str, user_id: str, rating: int, title: str,
                        pros: list[str], cons: list[str], body: str,
                        verified_purchase: bool = False) -> dict:
    if rating < 1 or rating > 5:
        return {"error": "Rating must be 1-5"}
    if len(title) < 5:
        return {"error": "Title too short (min 5 chars)"}
    return {"app_id": app_id, "user_id": user_id, "rating": rating, "title": title,
            "pros": pros, "cons": cons, "body": body, "verified_purchase": verified_purchase,
            "helpful_yes": 0, "helpful_no": 0, "status": "published", "error": None}


def compute_review_stats_v2(*, reviews: list[dict]) -> dict:
    if not reviews:
        return {"count": 0, "avg_rating": 0, "distribution": {}, "verified_pct": 0}
    dist = {str(i): 0 for i in range(1, 6)}
    verified = 0
    total_rating = 0
    for r in reviews:
        dist[str(r.get("rating", 0))] += 1
        total_rating += r.get("rating", 0)
        if r.get("verified_purchase"):
            verified += 1
    return {"count": len(reviews), "avg_rating": round(total_rating / len(reviews), 2),
            "distribution": dist, "verified_pct": round(verified / len(reviews) * 100, 1)}


def sort_reviews(*, reviews: list[dict], sort_by: str = "recent") -> list[dict]:
    if sort_by == "helpful":
        return sorted(reviews, key=lambda r: r.get("helpful_yes", 0), reverse=True)
    elif sort_by == "rating_high":
        return sorted(reviews, key=lambda r: -r.get("rating", 0))
    elif sort_by == "rating_low":
        return sorted(reviews, key=lambda r: r.get("rating", 0))
    return sorted(reviews, key=lambda r: r.get("created_at", ""), reverse=True)
