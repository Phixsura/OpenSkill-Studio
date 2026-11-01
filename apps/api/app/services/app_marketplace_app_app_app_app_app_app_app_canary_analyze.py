"""Deployment canary analyzer — analyze canary metrics for promotion decisions."""
from __future__ import annotations
import math


def analyze_canary_metrics(baseline: dict, canary: dict, thresholds: dict | None = None) -> dict:
    th = thresholds or {"error_rate_delta": 1.0, "latency_delta_pct": 25, "success_rate_min": 95}
    b_err = baseline.get("error_rate", 0)
    c_err = canary.get("error_rate", 0)
    err_delta = round(c_err - b_err, 3)
    b_lat = baseline.get("p99_ms", 0)
    c_lat = canary.get("p99_ms", 0)
    lat_delta_pct = round((c_lat - b_lat) / max(b_lat, 0.01) * 100, 1)
    c_success = canary.get("success_rate", 100)
    err_ok = err_delta <= th["error_rate_delta"]
    lat_ok = lat_delta_pct <= th["latency_delta_pct"]
    success_ok = c_success >= th["success_rate_min"]
    if err_ok and lat_ok and success_ok:
        verdict = "promote"
    elif not err_ok and not lat_ok:
        verdict = "rollback"
    else:
        verdict = "hold"
    confidence = sum([err_ok, lat_ok, success_ok]) / 3 * 100
    return {"verdict": verdict, "confidence_pct": round(confidence, 1),
            "error_delta": err_delta, "latency_delta_pct": lat_delta_pct,
            "success_rate": c_success, "checks": {"err_ok": err_ok, "lat_ok": lat_ok, "success_ok": success_ok}}
