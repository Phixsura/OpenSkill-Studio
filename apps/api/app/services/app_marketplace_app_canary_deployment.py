"""Canary deployment — gradual traffic shifting for safe version rollouts."""


def create_canary(*, app_id: str, stable_version: str, canary_version: str,
                    initial_pct: int = 5) -> dict:
    if initial_pct < 1 or initial_pct > 50:
        return {"error": "Initial canary percentage must be 1-50%"}
    return {"app_id": app_id, "stable": stable_version, "canary": canary_version,
            "canary_pct": initial_pct, "status": "active", "error": None}


def adjust_traffic(*, canary: dict, new_pct: int) -> dict:
    if new_pct < 0 or new_pct > 100:
        return {**canary, "error": "Percentage must be 0-100"}
    status = "promoted" if new_pct == 100 else "rolled_back" if new_pct == 0 else "active"
    return {**canary, "canary_pct": new_pct, "status": status, "error": None}


def evaluate_canary_health(*, canary_metrics: dict, stable_metrics: dict,
                              error_threshold: float = 2.0) -> dict:
    canary_err = canary_metrics.get("error_rate", 0)
    stable_err = stable_metrics.get("error_rate", 0)
    degraded = canary_err > stable_err * error_threshold
    canary_p99 = canary_metrics.get("p99_ms", 0)
    stable_p99 = stable_metrics.get("p99_ms", 0)
    slow = canary_p99 > stable_p99 * 1.5
    return {"healthy": not degraded and not slow, "auto_rollback": degraded,
            "canary_error_rate": canary_err, "stable_error_rate": stable_err,
            "recommendation": "rollback" if degraded else "promote" if not slow else "hold"}
