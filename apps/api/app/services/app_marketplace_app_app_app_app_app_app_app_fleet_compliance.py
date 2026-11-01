"""Fleet compliance score — aggregate compliance across controls."""
from __future__ import annotations
def fleet_compliance_score(controls: list[dict]) -> dict:
    passing = [c for c in controls if c.get("status") == "pass"]
    score = round(len(passing) / max(len(controls), 1) * 100, 1)
    return {"total": len(controls), "passing": len(passing),
            "failing": len(controls) - len(passing), "score": score,
            "grade": "A" if score >= 90 else ("B" if score >= 75 else "F")}
