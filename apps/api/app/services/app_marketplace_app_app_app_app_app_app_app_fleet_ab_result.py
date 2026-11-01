"""Fleet A/B test results — track experiment outcomes."""
from __future__ import annotations
def fleet_ab_results(experiments: list[dict]) -> dict:
    winners = [e for e in experiments if e.get("result") == "winner"]
    losers = [e for e in experiments if e.get("result") == "loser"]
    inconclusive = [e for e in experiments if e.get("result") == "inconclusive"]
    return {"total": len(experiments), "winners": len(winners), "losers": len(losers),
            "inconclusive": len(inconclusive), "win_rate": round(len(winners) / max(len(experiments), 1) * 100, 1)}
