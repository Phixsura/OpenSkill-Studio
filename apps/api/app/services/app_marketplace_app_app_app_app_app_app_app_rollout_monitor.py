"""Release rollout monitor — monitor progressive rollout health in real-time."""
from __future__ import annotations


def monitor_rollout(rollout: dict, metrics: dict) -> dict:
    current_pct = rollout.get("current_pct", 0)
    error_rate = metrics.get("error_rate_pct", 0)
    latency_p99 = metrics.get("p99_ms", 0)
    baseline_error = metrics.get("baseline_error_rate", 0)
    baseline_latency = metrics.get("baseline_p99_ms", 0)
    error_ok = error_rate <= baseline_error * 1.5 + 0.5
    latency_ok = latency_p99 <= baseline_latency * 1.3
    health = "good" if error_ok and latency_ok else "bad"
    recommendation = "continue" if health == "good" else ("pause" if current_pct < 50 else "rollback")
    return {"current_pct": current_pct, "health": health,
            "recommendation": recommendation,
            "error_ok": error_ok, "latency_ok": latency_ok,
            "error_rate": error_rate, "p99_ms": latency_p99}
