"""Health score — composite app health scoring system."""

import html

DIMENSIONS = {
    "reliability": {"weight": 0.3, "description": "Uptime and error rates"},
    "performance": {"weight": 0.25, "description": "Response times and throughput"},
    "security": {"weight": 0.25, "description": "Vulnerability and compliance"},
    "quality": {"weight": 0.2, "description": "Code quality and test coverage"},
}


def calculate_health_score(*, scores: dict[str, float]) -> dict:
    weighted_sum = 0
    details = []
    for dim, info in DIMENSIONS.items():
        score = min(100, max(0, scores.get(dim, 0)))
        weighted = score * info["weight"]
        weighted_sum += weighted
        details.append({"dimension": dim, "score": score, "weight": info["weight"],
                         "weighted": round(weighted, 1), "description": info["description"]})
    overall = round(weighted_sum, 1)
    grade = "A+" if overall >= 95 else "A" if overall >= 90 else "B" if overall >= 80 else "C" if overall >= 70 else "D" if overall >= 60 else "F"
    return {"overall": overall, "grade": grade, "details": details,
            "status": "healthy" if overall >= 80 else "degraded" if overall >= 60 else "critical"}
