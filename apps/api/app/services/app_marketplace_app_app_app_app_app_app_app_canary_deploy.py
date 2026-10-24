"""Canary deployment analyzer — evaluate canary vs baseline metrics."""
from __future__ import annotations


def analyze_canary(baseline: dict, canary: dict, thresholds: dict | None = None) -> dict:
    th = thresholds or {"error_rate_delta": 0.5, "latency_delta_pct": 20}
    err_base = baseline.get("error_rate", 0)
    err_canary = canary.get("error_rate", 0)
    err_delta = round(err_canary - err_base, 3)
    lat_base = baseline.get("p99_ms", 0)
    lat_canary = canary.get("p99_ms", 0)
    lat_delta_pct = round((lat_canary - lat_base) / max(lat_base, 0.01) * 100, 1)
    err_ok = err_delta <= th["error_rate_delta"]
    lat_ok = lat_delta_pct <= th["latency_delta_pct"]
    if err_ok and lat_ok:
        verdict = "promote"
    elif not err_ok and not lat_ok:
        verdict = "rollback"
    else:
        verdict = "hold"
    return {"verdict": verdict, "error_rate_delta": err_delta,
            "latency_delta_pct": lat_delta_pct, "err_ok": err_ok, "lat_ok": lat_ok,
            "baseline_traffic": baseline.get("requests", 0),
            "canary_traffic": canary.get("requests", 0)}
