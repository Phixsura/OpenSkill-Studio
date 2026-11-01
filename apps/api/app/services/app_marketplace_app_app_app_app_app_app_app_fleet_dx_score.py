"""Fleet DX score — developer experience across the platform."""
from __future__ import annotations
def fleet_dx_score(metrics: dict) -> dict:
    scores = [metrics.get("onboarding", 0), metrics.get("docs_quality", 0),
              metrics.get("sdk_quality", 0), metrics.get("api_consistency", 0)]
    avg = round(sum(scores) / max(len(scores), 1), 1)
    grade = "A" if avg >= 90 else ("B" if avg >= 75 else ("C" if avg >= 60 else "F"))
    return {"score": avg, "grade": grade, "metrics": metrics}
