"""Circuit breaker finite state machine — model circuit states and transitions."""
from __future__ import annotations


class CircuitFSM:
    STATES = ("closed", "open", "half_open")
    def __init__(self, failure_threshold: int = 5, success_threshold: int = 3, timeout_s: int = 30):
        self.state = "closed"
        self._failure_threshold = failure_threshold
        self._success_threshold = success_threshold
        self._timeout = timeout_s
        self._failures = 0
        self._successes = 0
        self._transitions: list[dict] = []

    def _transition(self, new_state: str, reason: str) -> None:
        self._transitions.append({"from": self.state, "to": new_state, "reason": reason})
        self.state = new_state

    def on_success(self) -> dict:
        if self.state == "half_open":
            self._successes += 1
            if self._successes >= self._success_threshold:
                self._transition("closed", "success_threshold_met")
                self._failures = 0
                self._successes = 0
        elif self.state == "closed":
            self._failures = max(0, self._failures - 1)
        return {"state": self.state, "failures": self._failures}

    def on_failure(self) -> dict:
        if self.state == "closed":
            self._failures += 1
            if self._failures >= self._failure_threshold:
                self._transition("open", "failure_threshold_met")
        elif self.state == "half_open":
            self._transition("open", "failure_in_half_open")
            self._successes = 0
        return {"state": self.state, "failures": self._failures}

    def on_timeout(self) -> dict:
        if self.state == "open":
            self._transition("half_open", "timeout_elapsed")
            self._successes = 0
        return {"state": self.state}

    def history(self) -> list[dict]:
        return list(self._transitions)
