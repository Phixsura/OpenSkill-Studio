"""Service mesh traffic replay — replay captured mesh traffic for testing."""
from __future__ import annotations


class MeshTrafficReplay:
    def __init__(self):
        self._captures: list[dict] = []
        self._replayed = 0

    def capture(self, source: str, destination: str, method: str, path: str,
                status: int, duration_ms: float) -> dict:
        entry = {"source": source, "destination": destination, "method": method,
                 "path": path, "status": status, "duration_ms": duration_ms,
                 "seq": len(self._captures) + 1}
        self._captures.append(entry)
        return entry

    def replay(self, from_seq: int = 1, to_seq: int | None = None,
               source_filter: str = "") -> dict:
        filtered = self._captures
        if source_filter:
            filtered = [c for c in filtered if c["source"] == source_filter]
        filtered = [c for c in filtered if c["seq"] >= from_seq]
        if to_seq:
            filtered = [c for c in filtered if c["seq"] <= to_seq]
        self._replayed += len(filtered)
        return {"replayed": len(filtered), "captures": filtered}

    def stats(self) -> dict:
        return {"captured": len(self._captures), "replayed": self._replayed}
