"""Platform health scorecard — weighted scoring across dimensions."""
from __future__ import annotations

DIMENSIONS = {
    "reliability": {"weight": 0.30, "target": 99.9},
    "performance": {"weight": 0.25, "target": 95},
    "security": {"weight": 0.20, "target": 100},
    "developer_experience": {"weight": 0.15, "target": 90},
    "cost_efficiency": {"weight": 0.10, "target": 85},
}


def calculate_scorecard(scores: dict[str, float]) -> dict:
    results = []
    weighted_total = 0
    for dim, config in DIMENSIONS.items():
        actual = scores.get(dim, 0)
        weighted = round(actual * config["weight"], 2)
        weighted_total += weighted
        met = actual >= config["target"]
        results.append({"dimension": dim, "score": actual, "target": config["target"],
                         "weight": config["weight"], "weighted": weighted, "met": met})
    total = round(weighted_total, 1)
    grade = "A+" if total >= 95 else "A" if total >= 90 else "B" if total >= 80 else "C" if total >= 70 else "D"
    met_count = sum(1 for r in results if r["met"])
    return {"total_score": total, "grade": grade, "dimensions": results,
            "targets_met": met_count, "targets_total": len(DIMENSIONS)}
