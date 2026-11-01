"""User feedback collector — collect, categorize, and analyze user feedback."""
from __future__ import annotations
import html


class FeedbackCollector:
    def __init__(self):
        self._feedback: list[dict] = []

    def submit(self, *, user_id: str, category: str, rating: int,
                message: str, page: str = "") -> dict:
        rating = max(1, min(5, rating))
        entry = {"user_id": user_id, "category": category,
                 "rating": rating, "message": html.escape(message[:1000]),
                 "page": page, "status": "new"}
        self._feedback.append(entry)
        return {"submitted": True, "rating": rating, "category": category}

    def summary(self) -> dict:
        total = len(self._feedback)
        if not total:
            return {"total": 0, "avg_rating": 0, "by_category": {}, "nps": 0}
        avg = round(sum(f["rating"] for f in self._feedback) / total, 1)
        by_cat: dict[str, dict] = {}
        promoters = detractors = 0
        for f in self._feedback:
            cat = f["category"]
            if cat not in by_cat:
                by_cat[cat] = {"count": 0, "total_rating": 0}
            by_cat[cat]["count"] += 1
            by_cat[cat]["total_rating"] += f["rating"]
            if f["rating"] >= 4:
                promoters += 1
            elif f["rating"] <= 2:
                detractors += 1
        nps = round((promoters - detractors) / total * 100)
        categories = {k: {"count": v["count"], "avg_rating": round(v["total_rating"] / v["count"], 1)}
                       for k, v in by_cat.items()}
        return {"total": total, "avg_rating": avg, "by_category": categories,
                "nps": nps, "promoters": promoters, "detractors": detractors}
