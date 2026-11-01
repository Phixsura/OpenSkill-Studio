"""Canary analysis engine — statistically compare canary vs baseline."""
from __future__ import annotations
import math


def analyze_canary(baseline: dict, canary: dict, significance: float = 0.05) -> dict:
    metrics = {}
    any_regression = False
    for metric in set(list(baseline.keys()) + list(canary.keys())):
        b_val = baseline.get(metric, 0)
        c_val = canary.get(metric, 0)
        if b_val == 0:
            continue
        delta_pct = round((c_val - b_val) / abs(b_val) * 100, 1)
        regression = delta_pct > 10  # >10% worse
        improvement = delta_pct < -5  # >5% better
        if regression:
            any_regression = True
        metrics[metric] = {"baseline": b_val, "canary": c_val, "delta_pct": delta_pct,
                            "regression": regression, "improvement": improvement}
    verdict = "fail" if any_regression else "pass"
    return {"metrics": metrics, "verdict": verdict, "has_regression": any_regression,
            "metrics_checked": len(metrics)}


def canary_recommendation(analysis: dict) -> dict:
    if analysis["verdict"] == "pass":
        return {"action": "promote", "reason": "All metrics within threshold"}
    regressions = [m for m, d in analysis["metrics"].items() if d.get("regression")]
    return {"action": "rollback", "reason": f"Regression in: {', '.join(regressions)}",
            "regressions": regressions}
