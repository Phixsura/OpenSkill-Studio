"""App health check v2 — comprehensive multi-dimensional health scoring."""


def compute_app_health_v2(*, availability: float, performance_ms: int, error_rate: float,
                             security_score: int, freshness_days: int) -> dict:
    dimensions = {
        "availability": min(100, availability),
        "performance": max(0, 100 - max(0, performance_ms - 100) / 10),
        "reliability": max(0, 100 - error_rate * 20),
        "security": security_score,
        "freshness": max(0, 100 - freshness_days * 2),
    }
    composite = round(sum(dimensions.values()) / len(dimensions), 1)
    status = "excellent" if composite >= 90 else "good" if composite >= 70 else "fair" if composite >= 50 else "poor"
    return {"composite": composite, "status": status, "dimensions": dimensions}
