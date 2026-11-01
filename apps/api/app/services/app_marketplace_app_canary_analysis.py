"""Canary analysis — compare canary vs baseline metrics for safe rollout."""


def analyze_canary(*, baseline: dict, canary: dict, thresholds: dict | None = None) -> dict:
    defaults = {"error_rate_max_diff": 0.5, "latency_max_diff_pct": 20, "success_rate_min": 99.0}
    t = {**defaults, **(thresholds or {})}
    checks = []

    # Error rate
    b_err = baseline.get("error_rate", 0)
    c_err = canary.get("error_rate", 0)
    err_diff = round(c_err - b_err, 3)
    checks.append({"metric": "error_rate", "baseline": b_err, "canary": c_err,
                    "diff": err_diff, "passed": err_diff <= t["error_rate_max_diff"]})

    # Latency
    b_lat = baseline.get("p95_latency_ms", 0)
    c_lat = canary.get("p95_latency_ms", 0)
    lat_diff_pct = round((c_lat - b_lat) / max(b_lat, 1) * 100, 1)
    checks.append({"metric": "p95_latency", "baseline": b_lat, "canary": c_lat,
                    "diff_pct": lat_diff_pct, "passed": lat_diff_pct <= t["latency_max_diff_pct"]})

    # Success rate
    c_success = canary.get("success_rate", 100)
    checks.append({"metric": "success_rate", "canary": c_success,
                    "threshold": t["success_rate_min"], "passed": c_success >= t["success_rate_min"]})

    all_passed = all(c["passed"] for c in checks)
    return {
        "verdict": "promote" if all_passed else "rollback",
        "checks": checks,
        "passed": sum(1 for c in checks if c["passed"]),
        "total": len(checks),
        "confidence": round(sum(1 for c in checks if c["passed"]) / len(checks) * 100),
    }
