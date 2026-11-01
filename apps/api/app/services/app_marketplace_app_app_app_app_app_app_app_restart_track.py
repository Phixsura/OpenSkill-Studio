"""Service restart tracker — track service restarts and crash loops."""
from __future__ import annotations
from collections import defaultdict


class RestartTracker:
    def __init__(self, crash_loop_threshold: int = 5):
        self._restarts: dict[str, list[dict]] = defaultdict(list)
        self._threshold = crash_loop_threshold

    def record_restart(self, service: str, reason: str, exit_code: int = 0) -> dict:
        entry = {"reason": reason, "exit_code": exit_code}
        self._restarts[service].append(entry)
        count = len(self._restarts[service])
        crash_loop = count >= self._threshold
        return {"service": service, "restart_count": count,
                "crash_loop": crash_loop, "reason": reason}

    def crash_loops(self) -> list[dict]:
        return [{"service": s, "restarts": len(r)}
                for s, r in self._restarts.items() if len(r) >= self._threshold]

    def stats(self) -> dict:
        total = sum(len(r) for r in self._restarts.values())
        loops = len(self.crash_loops())
        return {"total_restarts": total, "services_tracked": len(self._restarts),
                "crash_loops": loops}
