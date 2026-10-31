"""Operational readiness checker — verify all operational requirements are met."""
from __future__ import annotations


def check_readiness(requirements: list[dict]) -> dict:
    results = []
    for req in requirements:
        met = req.get("met", False)
        results.append({"name": req["name"], "category": req.get("category", "general"),
                        "met": met, "severity": req.get("severity", "required"),
                        "detail": req.get("detail", "")})
    required_met = all(r["met"] for r in results if r["severity"] == "required")
    total_met = sum(1 for r in results if r["met"])
    score = round(total_met / max(len(results), 1) * 100)
    return {"ready": required_met, "score": score,
            "met": total_met, "total": len(results),
            "blocking": [r["name"] for r in results if not r["met"] and r["severity"] == "required"],
            "requirements": results}


def readiness_categories(results: list[dict]) -> dict:
    by_cat: dict[str, dict] = {}
    for r in results:
        cat = r.get("category", "general")
        if cat not in by_cat:
            by_cat[cat] = {"met": 0, "total": 0}
        by_cat[cat]["total"] += 1
        if r["met"]:
            by_cat[cat]["met"] += 1
    return {cat: {**data, "pct": round(data["met"] / max(data["total"], 1) * 100)}
            for cat, data in by_cat.items()}
