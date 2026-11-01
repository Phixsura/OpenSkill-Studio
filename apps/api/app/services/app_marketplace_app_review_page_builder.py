"""App review page builder — compile app review/rating page data."""

def build_review_page(*, reviews: list[dict], average: float, count: int, distribution: dict) -> dict:
    return {"reviews": reviews, "average": round(average, 1), "count": count,
            "distribution": distribution, "has_reviews": count > 0}
