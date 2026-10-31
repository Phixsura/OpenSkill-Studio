"""Fleet canary analysis — automated canary release scoring."""
from __future__ import annotations
def fleet_canary_analysis(metrics: dict) -> dict:
    error_delta = metrics.get("error_rate_delta_pct", 0)
    latency_delta = metrics.get("latency_delta_pct", 0)
    score = round(100 - abs(error_delta) * 10 - abs(latency_delta) * 2, 1)
    verdict = "promote" if score >= 80 else ("hold" if score >= 50 else "rollback")
    return {"error_delta": error_delta, "latency_delta": latency_delta,
            "score": max(score, 0), "verdict": verdict}
