"""Circuit breaker — prevent cascading failures in microservices."""

from datetime import datetime, timedelta


STATES = {"closed", "open", "half_open"}


def create_circuit_breaker(*, name: str, failure_threshold: int = 5,
                              recovery_timeout_sec: int = 30,
                              success_threshold: int = 3) -> dict:
    return {
        "name": name,
        "state": "closed",
        "failure_count": 0,
        "success_count": 0,
        "failure_threshold": failure_threshold,
        "recovery_timeout_sec": recovery_timeout_sec,
        "success_threshold": success_threshold,
        "last_failure_at": None,
    }


def record_result(*, breaker: dict, success: bool) -> dict:
    state = breaker["state"]
    failure_count = breaker["failure_count"]
    success_count = breaker["success_count"]

    if success:
        if state == "half_open":
            success_count += 1
            if success_count >= breaker["success_threshold"]:
                return {**breaker, "state": "closed", "failure_count": 0, "success_count": 0}
            return {**breaker, "success_count": success_count}
        return {**breaker, "failure_count": max(failure_count - 1, 0)}
    else:
        failure_count += 1
        if failure_count >= breaker["failure_threshold"]:
            return {**breaker, "state": "open", "failure_count": failure_count,
                    "last_failure_at": datetime.utcnow().isoformat()}
        return {**breaker, "failure_count": failure_count}


def should_allow_request(*, breaker: dict) -> dict:
    if breaker["state"] == "closed":
        return {"allowed": True, "state": "closed"}
    if breaker["state"] == "open":
        last = breaker.get("last_failure_at")
        if last:
            elapsed = (datetime.utcnow() - datetime.fromisoformat(last)).total_seconds()
            if elapsed >= breaker["recovery_timeout_sec"]:
                return {"allowed": True, "state": "half_open", "reason": "Recovery timeout elapsed"}
        return {"allowed": False, "state": "open", "reason": "Circuit is open"}
    return {"allowed": True, "state": "half_open"}
