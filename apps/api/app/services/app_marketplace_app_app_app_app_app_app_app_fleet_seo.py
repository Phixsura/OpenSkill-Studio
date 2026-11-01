"""Fleet SEO score — track search engine optimization."""
from __future__ import annotations
def fleet_seo_score(pages: list[dict]) -> dict:
    scores = [p.get("seo_score", 0) for p in pages]
    avg = round(sum(scores) / max(len(scores), 1), 1)
    poor = [s for s in scores if s < 50]
    return {"total": len(pages), "avg_score": avg, "poor_pages": len(poor),
            "good": avg >= 80}
