"""Chaos engineering toolkit — inject failures for resilience testing."""
from __future__ import annotations
import secrets


FAULT_TYPES = {"latency", "error", "timeout", "cpu_spike", "memory_leak", "network_partition"}


def create_experiment(name: str, target: str, fault_type: str,
                       duration_sec: int = 60, magnitude: float = 1.0) -> dict:
    if fault_type not in FAULT_TYPES:
        return {"created": False, "error": f"unknown fault, use {sorted(FAULT_TYPES)}"}
    exp_id = f"chaos_{secrets.token_urlsafe(8)}"
    return {"created": True, "id": exp_id, "name": name, "target": target,
            "fault_type": fault_type, "duration_sec": duration_sec,
            "magnitude": magnitude, "status": "ready"}


def simulate_impact(experiment: dict, baseline: dict) -> dict:
    fault = experiment["fault_type"]
    mag = experiment["magnitude"]
    impact = dict(baseline)
    if fault == "latency":
        impact["p99_ms"] = round(baseline.get("p99_ms", 100) * (1 + mag), 1)
    elif fault == "error":
        impact["error_rate"] = round(baseline.get("error_rate", 0.1) + mag * 5, 2)
    elif fault == "timeout":
        impact["timeout_rate"] = round(mag * 10, 1)
    impact["degraded"] = True
    return {"baseline": baseline, "impact": impact, "fault_type": fault}


def experiment_report(experiment: dict, impact: dict) -> dict:
    resilient = impact["impact"].get("error_rate", 0) < 5
    return {"experiment": experiment["name"], "target": experiment["target"],
            "fault": experiment["fault_type"], "resilient": resilient,
            "recommendation": "system handled fault well" if resilient else "add fallback/circuit breaker"}
