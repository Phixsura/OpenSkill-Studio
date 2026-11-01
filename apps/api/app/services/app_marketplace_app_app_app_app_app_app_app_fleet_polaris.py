"""Fleet Polaris — track k8s best practices score."""
from __future__ import annotations
def fleet_polaris_score(checks: list[dict]) -> dict:
    passing = [c for c in checks if c.get("passed", True)]
    warning = [c for c in checks if c.get("severity") == "warning"]
    danger = [c for c in checks if c.get("severity") == "danger"]
    score = round(len(passing) / max(len(checks), 1) * 100, 1)
    return {"total": len(checks), "passing": len(passing), "warnings": len(warning),
            "dangers": len(danger), "score": score, "grade": "A" if score >= 90 else ("B" if score >= 75 else "C")}
