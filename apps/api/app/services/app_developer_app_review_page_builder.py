"""Review page builder — compile review submission page data."""

def build_review_page(*, app: dict, version: dict, review: dict | None) -> dict:
    return {"app_name": app.get("name"), "version": version.get("version"),
            "review_status": review.get("review_status") if review else "not_submitted",
            "submitted": review is not None, "reviewer": review.get("reviewer_id") if review else None}
