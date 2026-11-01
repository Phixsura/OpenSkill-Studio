"""Request logger — structured HTTP request logging with filtering."""
from __future__ import annotations
from collections import defaultdict


class RequestLogger:
    def __init__(self, max_entries: int = 10000):
        self._logs: list[dict] = []
        self._max = max_entries

    def log(self, method: str, path: str, status: int, duration_ms: float,
            user_id: str = "", ip: str = "") -> dict:
        entry = {"method": method, "path": path, "status": status,
                 "duration_ms": duration_ms, "user_id": user_id, "ip": ip}
        self._logs.append(entry)
        if len(self._logs) > self._max:
            self._logs = self._logs[-self._max:]
        return entry

    def query(self, status_gte: int = 0, path_prefix: str = "",
              limit: int = 50) -> list[dict]:
        results = self._logs
        if status_gte:
            results = [r for r in results if r["status"] >= status_gte]
        if path_prefix:
            results = [r for r in results if r["path"].startswith(path_prefix)]
        return results[-limit:]

    def stats(self) -> dict:
        by_status: dict[str, int] = defaultdict(int)
        for log in self._logs:
            bucket = f"{log['status'] // 100}xx"
            by_status[bucket] += 1
        return {"total": len(self._logs), "by_status": dict(by_status)}
