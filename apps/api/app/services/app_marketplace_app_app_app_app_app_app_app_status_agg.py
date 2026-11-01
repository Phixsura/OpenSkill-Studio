"""Platform status aggregator — combine all platform health signals."""
from __future__ import annotations


def aggregate_status(signals: dict) -> dict:
    scores = {"services": signals.get("services_healthy_pct", 100),
              "deploys": signals.get("deploy_success_pct", 100),
              "errors": max(0, 100 - signals.get("error_rate_pct", 0) * 10),
              "latency": 100 if signals.get("p99_ms", 0) < 500 else 50,
              "incidents": 100 if signals.get("open_incidents", 0) == 0 else 50}
    total = round(sum(scores.values()) / len(scores), 1)
    status = "operational" if total >= 95 else "degraded" if total >= 70 else "outage"
    return {"overall_score": total, "status": status, "scores": scores,
            "signals_checked": len(scores)}
