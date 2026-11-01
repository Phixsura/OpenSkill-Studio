"""Chaos engineering — inject faults to test app resilience."""

import random


def create_experiment(*, app_id: str, fault_type: str, target: str, duration_seconds: int = 60) -> dict:
    valid_faults = {"latency", "error", "timeout", "connection_drop", "cpu_spike"}
    if fault_type not in valid_faults:
        return {"error": f"Invalid fault type. Use: {', '.join(sorted(valid_faults))}"}
    return {"app_id": app_id, "fault_type": fault_type, "target": target,
            "duration_seconds": duration_seconds, "status": "ready", "error": None}


def simulate_fault(*, fault_type: str, config: dict) -> dict:
    effects = {
        "latency": {"added_ms": config.get("added_ms", 500), "affected_pct": config.get("pct", 50)},
        "error": {"status_code": config.get("status_code", 500), "affected_pct": config.get("pct", 30)},
        "timeout": {"timeout_ms": config.get("timeout_ms", 30000), "affected_pct": config.get("pct", 20)},
        "connection_drop": {"affected_pct": config.get("pct", 10)},
        "cpu_spike": {"target_pct": config.get("target_pct", 90)},
    }
    return {"fault_type": fault_type, "effect": effects.get(fault_type, {}), "active": True}


def evaluate_resilience(*, baseline: dict, during_fault: dict) -> dict:
    error_increase = during_fault.get("error_rate", 0) - baseline.get("error_rate", 0)
    latency_increase = during_fault.get("p99_ms", 0) - baseline.get("p99_ms", 0)
    grade = "A" if error_increase < 1 else "B" if error_increase < 5 else "C" if error_increase < 15 else "F"
    return {"grade": grade, "error_increase_pct": round(error_increase, 1),
            "latency_increase_ms": latency_increase, "resilient": grade in ("A", "B")}
