"""Progressive rollout — staged percentage-based rollout with auto-promotion."""


def create_rollout(*, app_id: str, version_id: str, stages: list[dict] | None = None) -> dict:
    default_stages = [
        {"pct": 5, "duration_hours": 2, "name": "canary"},
        {"pct": 25, "duration_hours": 4, "name": "early_adopters"},
        {"pct": 50, "duration_hours": 8, "name": "half"},
        {"pct": 100, "duration_hours": 0, "name": "full"},
    ]
    return {"app_id": app_id, "version_id": version_id,
            "stages": stages or default_stages, "current_stage": 0,
            "status": "active", "auto_promote": True}


def should_promote(*, current_metrics: dict, thresholds: dict) -> dict:
    errors_ok = current_metrics.get("error_rate", 0) <= thresholds.get("max_error_rate", 1)
    latency_ok = current_metrics.get("p99_ms", 0) <= thresholds.get("max_p99_ms", 500)
    promote = errors_ok and latency_ok
    return {"promote": promote, "errors_ok": errors_ok, "latency_ok": latency_ok,
            "reason": None if promote else "Metrics exceeded thresholds"}


def advance_rollout(*, rollout: dict) -> dict:
    idx = rollout["current_stage"] + 1
    stages = rollout["stages"]
    if idx >= len(stages):
        return {**rollout, "status": "completed", "current_stage": len(stages) - 1}
    return {**rollout, "current_stage": idx, "current_pct": stages[idx]["pct"]}
