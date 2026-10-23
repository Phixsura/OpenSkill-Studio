"""Platform health scorecard — unified score across all dimensions."""
from __future__ import annotations


def compute_scorecard(dimensions: list[dict]) -> dict:
    results = []
    total_weight = 0
    weighted_score = 0
    for d in dimensions:
        name = d["name"]
        score = max(0, min(100, d.get("score", 0)))
        weight = d.get("weight", 1)
        total_weight += weight
        weighted_score += score * weight
        status = "excellent" if score >= 90 else "good" if score >= 70 else \
                 "fair" if score >= 50 else "poor"
        results.append({"name": name, "score": score, "weight": weight,
                         "status": status, "details": d.get("details", "")})
    overall = round(weighted_score / max(total_weight, 1))
    overall_status = "excellent" if overall >= 90 else "good" if overall >= 70 else \
                     "fair" if overall >= 50 else "poor"
    poor_dims = [r["name"] for r in results if r["status"] == "poor"]
    return {
        "overall_score": overall, "overall_display": f"{overall}/100",
        "overall_status": overall_status,
        "dimensions": results, "dimension_count": len(results),
        "poor_dimensions": poor_dims, "needs_attention": len(poor_dims) > 0,
    }
