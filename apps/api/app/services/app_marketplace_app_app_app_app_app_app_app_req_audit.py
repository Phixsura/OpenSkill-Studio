"""Request audit logger — log all API requests for compliance."""
from __future__ import annotations
from collections import defaultdict


class RequestAuditLogger:
    def __init__(self, max_entries: int = 50000):
        self._logs: list[dict] = []
        self._max = max_entries

    def log(self, user_id: str, method: str, path: str, status: int,
            ip: str = "", user_agent: str = "") -> dict:
        entry = {"user_id": user_id, "method": method, "path": path,
                 "status": status, "ip": ip, "user_agent": user_agent}
        self._logs.append(entry)
        if len(self._logs) > self._max:
            self._logs = self._logs[-self._max:]
        return entry

    def query(self, user_id: str = "", path_prefix: str = "",
              status_gte: int = 0, limit: int = 50) -> list[dict]:
        results = self._logs
        if user_id:
            results = [r for r in results if r["user_id"] == user_id]
        if path_prefix:
            results = [r for r in results if r["path"].startswith(path_prefix)]
        if status_gte:
            results = [r for r in results if r["status"] >= status_gte]
        return results[-limit:]

    def stats(self) -> dict:
        by_user: dict[str, int] = defaultdict(int)
        for log in self._logs:
            by_user[log["user_id"]] += 1
        return {"total": len(self._logs), "unique_users": len(by_user),
                "top_users": sorted(by_user.items(), key=lambda x: -x[1])[:5]}
