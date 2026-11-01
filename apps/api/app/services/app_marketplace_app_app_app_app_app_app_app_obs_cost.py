"""Observability cost tracker — track costs of logging, metrics, tracing."""
from __future__ import annotations


def calculate_obs_costs(metrics: dict, logs: dict, traces: dict) -> dict:
    metrics_cost = round(metrics.get("series", 0) * metrics.get("cost_per_series", 0.01), 2)
    logs_cost = round(logs.get("gb_ingested", 0) * logs.get("cost_per_gb", 0.50), 2)
    traces_cost = round(traces.get("spans_millions", 0) * traces.get("cost_per_million", 2.00), 2)
    total = round(metrics_cost + logs_cost + traces_cost, 2)
    return {"metrics_cost": metrics_cost, "logs_cost": logs_cost,
            "traces_cost": traces_cost, "total_cost": total,
            "display": f"${total:,.2f}/mo",
            "breakdown_pct": {
                "metrics": round(metrics_cost / max(total, 0.01) * 100),
                "logs": round(logs_cost / max(total, 0.01) * 100),
                "traces": round(traces_cost / max(total, 0.01) * 100),
            }}


def suggest_optimizations(costs: dict) -> list[dict]:
    suggestions = []
    bp = costs.get("breakdown_pct", {})
    if bp.get("logs", 0) > 50:
        suggestions.append({"area": "logs", "action": "Reduce log verbosity or add sampling"})
    if bp.get("traces", 0) > 40:
        suggestions.append({"area": "traces", "action": "Lower trace sample rate"})
    if costs.get("total_cost", 0) > 1000:
        suggestions.append({"area": "overall", "action": "Review retention policies"})
    return suggestions
