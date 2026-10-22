"""Rate limit config — configurable rate limiting per app endpoint."""


def create_rate_limit_rule(*, app_id: str, endpoint: str, requests_per_minute: int,
                              burst: int | None = None) -> dict:
    if requests_per_minute < 1:
        return {"error": "Rate must be at least 1 request per minute"}
    if requests_per_minute > 10000:
        return {"error": "Maximum rate is 10,000 requests per minute"}
    return {
        "app_id": app_id, "endpoint": endpoint,
        "requests_per_minute": requests_per_minute,
        "burst": burst or min(requests_per_minute * 2, 1000),
        "error": None,
    }


def evaluate_rate_limit(*, rule: dict, current_count: int, window_start_epoch: int,
                           now_epoch: int) -> dict:
    window_seconds = 60
    elapsed = now_epoch - window_start_epoch
    if elapsed >= window_seconds:
        return {"allowed": True, "remaining": rule["requests_per_minute"], "reset_in": 0}
    remaining = max(0, rule["requests_per_minute"] - current_count)
    return {
        "allowed": remaining > 0, "remaining": remaining,
        "reset_in": window_seconds - elapsed,
        "retry_after": None if remaining > 0 else window_seconds - elapsed,
    }
