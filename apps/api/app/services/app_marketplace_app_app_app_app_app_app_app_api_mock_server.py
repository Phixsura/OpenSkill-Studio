"""API mock server — define mock endpoints for testing and development."""
from __future__ import annotations
import json
import re


class MockServer:
    def __init__(self):
        self._mocks: list[dict] = []

    def add_mock(self, *, method: str, path: str, status: int = 200,
                  body: dict | None = None, delay_ms: int = 0,
                  headers: dict | None = None) -> dict:
        mock = {"method": method.upper(), "path": path, "status": status,
                "body": body or {}, "delay_ms": delay_ms,
                "headers": headers or {"Content-Type": "application/json"},
                "hit_count": 0}
        self._mocks.append(mock)
        return {"added": True, "method": method.upper(), "path": path, "index": len(self._mocks) - 1}

    def match(self, method: str, path: str) -> dict:
        method = method.upper()
        for mock in self._mocks:
            if mock["method"] == method and self._path_match(mock["path"], path):
                mock["hit_count"] += 1
                return {"matched": True, "status": mock["status"],
                        "body": mock["body"], "headers": mock["headers"],
                        "delay_ms": mock["delay_ms"]}
        return {"matched": False, "status": 404, "body": {"error": "No mock matched"}}

    def stats(self) -> dict:
        return {"total_mocks": len(self._mocks),
                "mocks": [{"method": m["method"], "path": m["path"],
                           "hits": m["hit_count"]} for m in self._mocks],
                "total_hits": sum(m["hit_count"] for m in self._mocks)}

    @staticmethod
    def _path_match(pattern: str, path: str) -> bool:
        regex = re.sub(r":(\w+)", r"[^/]+", pattern)
        return bool(re.fullmatch(regex, path))
