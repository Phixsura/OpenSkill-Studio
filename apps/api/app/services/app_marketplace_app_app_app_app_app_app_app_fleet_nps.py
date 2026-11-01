"""Fleet platform NPS — net promoter score tracking."""
from __future__ import annotations
def fleet_platform_nps(responses: list[dict]) -> dict:
    promoters = [r for r in responses if r.get("score", 0) >= 9]
    detractors = [r for r in responses if r.get("score", 0) <= 6]
    nps = round((len(promoters) - len(detractors)) / max(len(responses), 1) * 100, 1)
    return {"responses": len(responses), "promoters": len(promoters),
            "detractors": len(detractors), "nps": nps, "excellent": nps >= 50}
