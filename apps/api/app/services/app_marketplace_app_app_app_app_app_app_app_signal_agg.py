"""Health signal aggregator — aggregate health signals from multiple sources."""
from __future__ import annotations


def aggregate_signals(signals: list[dict]) -> dict:
    weights = {"metrics": 30, "logs": 20, "traces": 20, "synthetic": 15, "user_reports": 15}
    scores: dict[str, float] = {}
    for signal in signals:
        source = signal["source"]
        health = signal.get("health_pct", 100)
        weight = weights.get(source, 10)
        scores[source] = health * weight / 100
    total_weight = sum(weights.get(s["source"], 10) for s in signals)
    composite = round(sum(scores.values()) / max(total_weight, 0.01) * 100, 1)
    status = "healthy" if composite >= 95 else ("degraded" if composite >= 70 else "critical")
    return {"composite_score": composite, "status": status,
            "signals": {s["source"]: s.get("health_pct", 100) for s in signals},
            "sources": len(signals)}
