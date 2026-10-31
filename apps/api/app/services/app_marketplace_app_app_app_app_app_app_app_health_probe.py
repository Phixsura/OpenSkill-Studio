"""Health check probe — liveness, readiness, and startup probes."""
from __future__ import annotations
import time


class HealthProbe:
    def __init__(self):
        self._checks: dict[str, callable] = {}
        self._startup_complete = False

    def register_check(self, name: str, check_fn: callable, probe_type: str = "readiness") -> dict:
        self._checks[name] = {"fn": check_fn, "type": probe_type}
        return {"name": name, "type": probe_type, "registered": True}

    def mark_started(self) -> dict:
        self._startup_complete = True
        return {"startup_complete": True}

    def liveness(self) -> dict:
        return {"status": "ok", "probe": "liveness"}

    def readiness(self) -> dict:
        if not self._startup_complete:
            return {"status": "not_ready", "reason": "startup_incomplete"}
        failures = []
        for name, check in self._checks.items():
            if check["type"] != "readiness":
                continue
            try:
                result = check["fn"]()
                if not result:
                    failures.append(name)
            except Exception:
                failures.append(name)
        if failures:
            return {"status": "not_ready", "failed_checks": failures}
        return {"status": "ready"}

    def startup(self) -> dict:
        return {"status": "complete" if self._startup_complete else "in_progress"}
