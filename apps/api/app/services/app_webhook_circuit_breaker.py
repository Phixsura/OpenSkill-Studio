"""Webhook circuit breaker — stop delivery to consistently failing endpoints."""

from collections import defaultdict
from datetime import UTC, datetime, timedelta

_failure_counts: dict[str, int] = defaultdict(int)
_circuit_state: dict[str, dict] = {}

FAILURE_THRESHOLD = 10
RESET_TIMEOUT_SECONDS = 300  # 5 minutes


def record_failure(endpoint: str) -> None:
    _failure_counts[endpoint] += 1
    if _failure_counts[endpoint] >= FAILURE_THRESHOLD:
        _circuit_state[endpoint] = {
            "state": "open",
            "opened_at": datetime.now(UTC).isoformat(),
            "reset_at": (datetime.now(UTC) + timedelta(seconds=RESET_TIMEOUT_SECONDS)).isoformat(),
        }


def record_success(endpoint: str) -> None:
    _failure_counts[endpoint] = 0
    _circuit_state.pop(endpoint, None)


def is_circuit_open(endpoint: str) -> bool:
    state = _circuit_state.get(endpoint)
    if not state:
        return False
    reset_at = datetime.fromisoformat(state["reset_at"])
    if datetime.now(UTC) > reset_at:
        # Half-open: allow one attempt
        _circuit_state.pop(endpoint, None)
        _failure_counts[endpoint] = FAILURE_THRESHOLD - 1
        return False
    return True


def get_circuit_status(endpoint: str) -> str:
    if endpoint not in _circuit_state:
        return "closed"
    state = _circuit_state[endpoint]
    reset_at = datetime.fromisoformat(state["reset_at"])
    if datetime.now(UTC) > reset_at:
        return "half-open"
    return "open"


def reset_circuit(endpoint: str) -> None:
    _failure_counts.pop(endpoint, None)
    _circuit_state.pop(endpoint, None)
