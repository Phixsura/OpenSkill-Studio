"""API mock server — define mock endpoints with configurable responses."""
from __future__ import annotations


class MockServer:
    def __init__(self):
        self._mocks: dict[str, dict] = {}
        self._call_count: dict[str, int] = {}

    def register(self, method: str, path: str, status: int = 200,
                 body: dict | None = None, delay_ms: int = 0) -> dict:
        key = f"{method} {path}"
        self._mocks[key] = {"method": method, "path": path, "status": status,
                             "body": body or {}, "delay_ms": delay_ms}
        self._call_count[key] = 0
        return {"registered": True, "key": key}

    def handle(self, method: str, path: str) -> dict:
        key = f"{method} {path}"
        mock = self._mocks.get(key)
        if not mock:
            return {"status": 404, "body": {"error": "no_mock"}, "mocked": False}
        self._call_count[key] += 1
        return {"status": mock["status"], "body": mock["body"],
                "mocked": True, "delay_ms": mock["delay_ms"],
                "call_number": self._call_count[key]}

    def list_mocks(self) -> list[dict]:
        return [{"key": k, **v, "calls": self._call_count.get(k, 0)}
                for k, v in self._mocks.items()]

    def stats(self) -> dict:
        total_calls = sum(self._call_count.values())
        return {"mocks": len(self._mocks), "total_calls": total_calls}
