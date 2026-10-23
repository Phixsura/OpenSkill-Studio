"""Health scorecard — comprehensive health grade combining all dimensions."""


def compute_health_scorecard(*, availability: float, performance: dict, security: dict,
                                compliance: dict, developer_experience: dict) -> dict:
    scores = {
        "availability": min(100, availability),
        "performance": max(0, 100 - max(0, performance.get("p99_ms", 0) - 100) / 10),
        "security": security.get("score", 0),
        "compliance": compliance.get("score", 0),
        "dx": developer_experience.get("score", 0),
    }
    weights = {"availability": 0.25, "performance": 0.20, "security": 0.25,
               "compliance": 0.15, "dx": 0.15}
    composite = sum(scores[k] * weights[k] for k in weights)
    grade = "A+" if composite >= 95 else "A" if composite >= 90 else "B" if composite >= 75 else "C" if composite >= 60 else "D" if composite >= 40 else "F"
    weakest = min(scores.items(), key=lambda x: x[1])
    return {
        "composite_score": round(composite, 1), "grade": grade,
        "dimensions": {k: round(v, 1) for k, v in scores.items()},
        "weakest_dimension": weakest[0], "improvement_area": weakest[0],
    }


def get_improvement_recommendations(*, scorecard: dict) -> list[str]:
    recs = []
    dims = scorecard.get("dimensions", {})
    if dims.get("availability", 100) < 99.9:
        recs.append("Improve availability — add health checks and redundancy")
    if dims.get("performance", 100) < 80:
        recs.append("Optimize performance — reduce P99 latency with caching")
    if dims.get("security", 100) < 80:
        recs.append("Strengthen security — complete all security checks")
    if dims.get("compliance", 100) < 80:
        recs.append("Improve compliance — address critical compliance gaps")
    if dims.get("dx", 100) < 80:
        recs.append("Improve DX — add documentation and quickstart guides")
    return recs or ["Excellent! All dimensions are strong."]
