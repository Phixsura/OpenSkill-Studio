"""Endpoint maturity model — assess endpoint maturity across dimensions."""
from __future__ import annotations


def assess_maturity(endpoint: dict) -> dict:
    dimensions = {
        "documentation": 1 if endpoint.get("has_docs") else 0,
        "testing": 1 if endpoint.get("has_tests") else 0,
        "monitoring": 1 if endpoint.get("has_monitoring") else 0,
        "error_handling": 1 if endpoint.get("has_error_handling") else 0,
        "rate_limiting": 1 if endpoint.get("has_rate_limit") else 0,
        "versioning": 1 if endpoint.get("has_versioning") else 0,
        "auth": 1 if endpoint.get("has_auth") else 0,
        "caching": 1 if endpoint.get("has_caching") else 0,
    }
    score = sum(dimensions.values())
    total = len(dimensions)
    pct = round(score / total * 100)
    level = "mature" if pct >= 88 else ("growing" if pct >= 63 else ("basic" if pct >= 38 else "initial"))
    return {"endpoint": endpoint.get("path", ""), "score": score, "total": total,
            "pct": pct, "level": level, "dimensions": dimensions}
