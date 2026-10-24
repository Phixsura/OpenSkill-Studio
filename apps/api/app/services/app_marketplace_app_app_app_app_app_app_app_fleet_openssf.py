"""Fleet OpenSSF Scorecard — track supply chain security score."""
from __future__ import annotations
def fleet_openssf_scorecard(repos: list[dict]) -> dict:
    scores = [r.get("score", 0) for r in repos]
    avg = round(sum(scores) / max(len(scores), 1), 1)
    low = [s for s in scores if s < 5]
    return {"total": len(repos), "avg_score": avg, "low_score": len(low),
            "grade": "A" if avg >= 8 else ("B" if avg >= 6 else "C")}
