"""Complete app review page — all reviews with stats, replies, and moderation."""


def build_complete_review_page_v2(*, app: dict, reviews: list[dict], stats: dict,
                                      developer_reply_rate: float, sort_by: str = "recent",
                                      page: int = 1, per_page: int = 10) -> dict:
    # Sort
    if sort_by == "helpful":
        reviews = sorted(reviews, key=lambda r: r.get("helpful_yes", 0), reverse=True)
    elif sort_by == "highest":
        reviews = sorted(reviews, key=lambda r: -r.get("rating", 0))
    elif sort_by == "lowest":
        reviews = sorted(reviews, key=lambda r: r.get("rating", 0))
    total = len(reviews)
    start = (page - 1) * per_page
    page_reviews = reviews[start:start + per_page]
    return {
        "page_type": "app_reviews",
        "app": {"id": app["id"], "name": app["name"]},
        "stats": stats,
        "developer_reply_rate": developer_reply_rate,
        "reviews": page_reviews,
        "pagination": {"page": page, "total": total, "total_pages": max(1, (total + per_page - 1) // per_page)},
        "sort_options": ["recent", "helpful", "highest", "lowest"],
        "can_review": True,
    }
