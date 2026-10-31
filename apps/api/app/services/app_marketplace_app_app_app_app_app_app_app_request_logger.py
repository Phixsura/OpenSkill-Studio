"""API request logger — structured request/response logging for debugging."""
from __future__ import annotations
import secrets


class RequestLogger:
    def __init__(self, *, max_entries: int = 1000):
        self._entries: list[dict] = []
        self._max = max_entries

    def log(self, *, method: str, path: str, status: int, duration_ms: int,
            request_size: int = 0, response_size: int = 0,
            user_id: str = "", ip: str = "") -> dict:
        rid = f"req_{secrets.token_hex(8)}"
        entry = {"id": rid, "method": method, "path": path, "status": status,
                 "duration_ms": duration_ms, "request_size": request_size,
                 "response_size": response_size, "user_id": user_id, "ip": ip,
                 "error": status >= 400}
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return {"id": rid, "logged": True}

    def query(self, *, status_min: int | None = None, path_prefix: str | None = None,
               limit: int = 50) -> list[dict]:
        results = self._entries
        if status_min:
            results = [e for e in results if e["status"] >= status_min]
        if path_prefix:
            results = [e for e in results if e["path"].startswith(path_prefix)]
        return list(reversed(results[-limit:]))

    def stats(self) -> dict:
        total = len(self._entries)
        errors = sum(1 for e in self._entries if e["error"])
        avg_dur = round(sum(e["duration_ms"] for e in self._entries) / max(total, 1), 1)
        return {"total": total, "errors": errors,
                "error_rate": round(errors / max(total, 1) * 100, 1),
                "avg_duration_ms": avg_dur}
