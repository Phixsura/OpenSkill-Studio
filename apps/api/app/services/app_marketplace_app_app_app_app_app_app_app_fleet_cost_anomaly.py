"""Fleet cost anomaly — detect cost spikes across services."""
from __future__ import annotations
def detect_cost_anomaly(costs: list[float], threshold_mult: float = 2.0) -> dict:
    if len(costs) < 3:
        return {"anomaly": False, "latest": costs[-1] if costs else 0, "baseline": 0}
    baseline = sum(costs[:-1]) / len(costs[:-1])
    latest = costs[-1]
    return {"anomaly": latest > baseline * threshold_mult, "latest": latest,
            "baseline": round(baseline, 2), "ratio": round(latest / max(baseline, 0.01), 2)}
