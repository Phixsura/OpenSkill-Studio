"""Service maturity model — assess service operational maturity."""
from __future__ import annotations

DIMENSIONS = {
    "observability": {"description": "Logging, metrics, tracing", "max": 5},
    "reliability": {"description": "SLOs, error budgets, chaos testing", "max": 5},
    "security": {"description": "AuthN, AuthZ, encryption, scanning", "max": 5},
    "automation": {"description": "CI/CD, IaC, auto-scaling", "max": 5},
    "documentation": {"description": "API docs, runbooks, architecture", "max": 5},
}


def assess_maturity(service: str, scores: dict[str, int]) -> dict:
    results = []
    total = 0
    max_total = 0
    for dim, config in DIMENSIONS.items():
        score = min(scores.get(dim, 0), config["max"])
        total += score
        max_total += config["max"]
        results.append({"dimension": dim, "score": score, "max": config["max"],
                         "description": config["description"]})
    pct = round(total / max(max_total, 1) * 100)
    level = "L5" if pct >= 90 else "L4" if pct >= 75 else "L3" if pct >= 60 else "L2" if pct >= 40 else "L1"
    return {"service": service, "dimensions": results, "total_score": total,
            "max_score": max_total, "maturity_pct": pct, "level": level}
