"""App review report — generate periodic review digest reports."""


def generate_review_report(*, app_name: str, period: str, reviews: list[dict]) -> dict:
    if not reviews:
        return {"app_name": app_name, "period": period, "total": 0, "summary": "No reviews"}
    total = len(reviews)
    avg = round(sum(r.get("rating", 0) for r in reviews) / total, 1)
    five_stars = sum(1 for r in reviews if r.get("rating") == 5)
    one_stars = sum(1 for r in reviews if r.get("rating") == 1)
    responded = sum(1 for r in reviews if r.get("responded"))
    response_rate = round(responded / total * 100, 1)
    highlights = [r for r in reviews if r.get("rating", 0) >= 4][:3]
    concerns = [r for r in reviews if r.get("rating", 0) <= 2][:3]
    return {
        "app_name": app_name,
        "period": period,
        "total": total,
        "avg_rating": avg,
        "five_star_count": five_stars,
        "one_star_count": one_stars,
        "response_rate": response_rate,
        "highlights": [{"text": h.get("text", ""), "rating": h.get("rating")} for h in highlights],
        "concerns": [{"text": c.get("text", ""), "rating": c.get("rating")} for c in concerns],
    }
