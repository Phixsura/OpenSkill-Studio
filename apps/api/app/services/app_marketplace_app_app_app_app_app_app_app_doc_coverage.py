"""API documentation coverage — measure how well APIs are documented."""
from __future__ import annotations


def measure_coverage(endpoints: list[dict]) -> dict:
    total = len(endpoints)
    has_description = sum(1 for e in endpoints if e.get("description"))
    has_examples = sum(1 for e in endpoints if e.get("examples"))
    has_params_doc = sum(1 for e in endpoints if e.get("params_documented"))
    has_error_doc = sum(1 for e in endpoints if e.get("errors_documented"))
    scores = {
        "description": round(has_description / max(total, 1) * 100, 1),
        "examples": round(has_examples / max(total, 1) * 100, 1),
        "parameters": round(has_params_doc / max(total, 1) * 100, 1),
        "error_codes": round(has_error_doc / max(total, 1) * 100, 1),
    }
    overall = round(sum(scores.values()) / len(scores), 1)
    return {"overall_pct": overall, "scores": scores, "total_endpoints": total,
            "grade": "A" if overall >= 90 else ("B" if overall >= 70 else ("C" if overall >= 50 else "F"))}
