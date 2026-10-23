"""Canary deployment manager — gradual rollout with metrics."""
from __future__ import annotations


def create_canary(service: str, baseline_version: str, canary_version: str,
                  initial_pct: float = 5.0) -> dict:
    return {"service": service, "baseline": baseline_version,
            "canary": canary_version, "traffic_pct": initial_pct,
            "status": "running", "phase": "initial"}


def evaluate_canary(canary: dict, baseline_metrics: dict, canary_metrics: dict,
                    error_threshold: float = 1.0) -> dict:
    b_err = baseline_metrics.get("error_rate", 0)
    c_err = canary_metrics.get("error_rate", 0)
    b_lat = baseline_metrics.get("p99_latency_ms", 0)
    c_lat = canary_metrics.get("p99_latency_ms", 0)
    err_ok = c_err <= b_err + error_threshold
    lat_ok = c_lat <= b_lat * 1.2  # 20% tolerance
    healthy = err_ok and lat_ok
    action = "promote" if healthy and canary["traffic_pct"] >= 50 else "advance" if healthy else "rollback"
    return {"service": canary["service"], "healthy": healthy,
            "error_ok": err_ok, "latency_ok": lat_ok,
            "action": action, "current_pct": canary["traffic_pct"]}


def advance_canary(canary: dict, step_pct: float = 10.0) -> dict:
    new_pct = min(100.0, canary["traffic_pct"] + step_pct)
    canary["traffic_pct"] = new_pct
    if new_pct >= 100:
        canary["status"] = "promoted"
        canary["phase"] = "complete"
    elif new_pct >= 50:
        canary["phase"] = "majority"
    else:
        canary["phase"] = "expanding"
    return canary
