"""Chaos testing — inject failures to test app resilience."""

import secrets


FAULT_TYPES = {
    "latency": {"label": "Latency injection", "description": "Add artificial delay"},
    "error_rate": {"label": "Error rate", "description": "Return errors for a percentage of requests"},
    "cpu_stress": {"label": "CPU stress", "description": "Consume CPU resources"},
    "memory_pressure": {"label": "Memory pressure", "description": "Allocate memory"},
    "network_partition": {"label": "Network partition", "description": "Block network to dependencies"},
}


def create_experiment(*, app_id: str, fault_type: str, config: dict,
                        duration_sec: int = 300) -> dict:
    if fault_type not in FAULT_TYPES:
        return {"error": f"Unknown fault type. Valid: {', '.join(sorted(FAULT_TYPES))}"}
    if duration_sec > 3600:
        return {"error": "Max duration is 3600 seconds"}
    return {
        "experiment_id": f"chaos_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "fault_type": fault_type,
        "fault_info": FAULT_TYPES[fault_type],
        "config": config,
        "duration_sec": duration_sec,
        "status": "pending",
        "safety_stop": True,
    }


def evaluate_resilience(*, before: dict, during: dict, after: dict) -> dict:
    recovery_time = after.get("recovery_time_sec", 0)
    error_spike = during.get("error_rate", 0) - before.get("error_rate", 0)
    latency_spike = during.get("p95_ms", 0) - before.get("p95_ms", 0)
    recovered = after.get("error_rate", 0) <= before.get("error_rate", 0) * 1.1
    score = 100
    if error_spike > 10:
        score -= 30
    if latency_spike > 500:
        score -= 20
    if recovery_time > 60:
        score -= 20
    if not recovered:
        score -= 30
    return {
        "resilience_score": max(score, 0),
        "error_spike_pct": round(error_spike, 2),
        "latency_spike_ms": round(latency_spike, 1),
        "recovery_time_sec": recovery_time,
        "fully_recovered": recovered,
        "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "F",
    }
