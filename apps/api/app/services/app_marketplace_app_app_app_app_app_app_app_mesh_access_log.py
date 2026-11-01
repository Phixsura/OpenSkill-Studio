"""Service mesh access log — structured access logs for mesh traffic."""
from __future__ import annotations
from collections import defaultdict


class MeshAccessLog:
    def __init__(self, max_entries: int = 5000):
        self._entries: list[dict] = []
        self._max = max_entries

    def log(self, source: str, destination: str, method: str, path: str,
            status: int, duration_ms: float) -> dict:
        entry = {"source": source, "destination": destination, "method": method,
                 "path": path, "status": status, "duration_ms": duration_ms}
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return entry

    def query(self, source: str = "", destination: str = "",
              status_gte: int = 0, limit: int = 50) -> list[dict]:
        results = self._entries
        if source:
            results = [e for e in results if e["source"] == source]
        if destination:
            results = [e for e in results if e["destination"] == destination]
        if status_gte:
            results = [e for e in results if e["status"] >= status_gte]
        return results[-limit:]

    def stats(self) -> dict:
        by_pair: dict[str, int] = defaultdict(int)
        errors = 0
        for e in self._entries:
            by_pair[f"{e['source']}→{e['destination']}"] += 1
            if e["status"] >= 500:
                errors += 1
        return {"total": len(self._entries), "errors": errors,
                "unique_pairs": len(by_pair)}
