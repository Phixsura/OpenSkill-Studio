"""Circuit breaker dashboard — monitor circuit breaker states across app endpoints."""

STATES = {"closed", "open", "half_open"}


def get_circuit_status(*, failure_count: int, threshold: int, last_failure_ago_seconds: int,
                         recovery_timeout: int = 30) -> dict:
    if failure_count >= threshold:
        if last_failure_ago_seconds < recovery_timeout:
            return {"state": "open", "reason": f"{failure_count} failures exceeded threshold of {threshold}"}
        return {"state": "half_open", "reason": "Recovery timeout elapsed, testing..."}
    return {"state": "closed", "reason": None}


def build_circuit_dashboard(*, circuits: list[dict]) -> dict:
    by_state = {"closed": 0, "open": 0, "half_open": 0}
    for c in circuits:
        state = c.get("state", "closed")
        by_state[state] = by_state.get(state, 0) + 1
    health = "healthy" if by_state["open"] == 0 else "degraded" if by_state["open"] < 3 else "critical"
    return {"circuits": circuits, "by_state": by_state, "total": len(circuits), "health": health}


def should_allow_request(*, circuit: dict) -> bool:
    return circuit.get("state") != "open"
