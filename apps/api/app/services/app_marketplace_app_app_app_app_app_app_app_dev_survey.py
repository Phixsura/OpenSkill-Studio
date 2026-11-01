"""Developer satisfaction survey — measure developer experience."""
from __future__ import annotations


def analyze_survey(responses: list[dict]) -> dict:
    if not responses:
        return {"respondents": 0}
    categories = {}
    for r in responses:
        for cat, score in r.get("scores", {}).items():
            categories.setdefault(cat, []).append(score)
    results = {}
    for cat, scores in categories.items():
        avg = round(sum(scores) / len(scores), 1)
        results[cat] = {"avg": avg, "responses": len(scores),
                         "satisfied": sum(1 for s in scores if s >= 4)}
    overall = round(sum(r["avg"] for r in results.values()) / max(len(results), 1), 1)
    nps_scores = [r.get("nps", 5) for r in responses]
    promoters = sum(1 for s in nps_scores if s >= 9)
    detractors = sum(1 for s in nps_scores if s <= 6)
    nps = round((promoters - detractors) / len(nps_scores) * 100)
    return {"respondents": len(responses), "categories": results,
            "overall_satisfaction": overall, "nps": nps}
