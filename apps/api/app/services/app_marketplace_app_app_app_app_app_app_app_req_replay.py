"""Request replay engine — capture and replay HTTP requests for debugging."""
from __future__ import annotations


class RequestReplayEngine:
    def __init__(self, max_buffer: int = 1000):
        self._buffer: list[dict] = []
        self._max = max_buffer
        self._replayed = 0

    def capture(self, method: str, path: str, headers: dict | None = None,
                body: str = "", status: int = 200) -> dict:
        entry = {"method": method, "path": path, "headers": headers or {},
                 "body": body, "status": status, "seq": len(self._buffer) + 1}
        self._buffer.append(entry)
        if len(self._buffer) > self._max:
            self._buffer = self._buffer[-self._max:]
        return {"captured": True, "seq": entry["seq"]}

    def replay(self, from_seq: int = 1, to_seq: int | None = None,
               filter_path: str = "") -> dict:
        filtered = self._buffer
        if filter_path:
            filtered = [r for r in filtered if r["path"].startswith(filter_path)]
        filtered = [r for r in filtered if r["seq"] >= from_seq]
        if to_seq:
            filtered = [r for r in filtered if r["seq"] <= to_seq]
        self._replayed += len(filtered)
        return {"replayed": len(filtered), "requests": filtered}

    def stats(self) -> dict:
        return {"captured": len(self._buffer), "replayed": self._replayed, "max_buffer": self._max}
