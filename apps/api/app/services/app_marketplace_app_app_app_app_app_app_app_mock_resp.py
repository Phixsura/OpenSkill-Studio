"""API mock response builder — generate realistic mock API responses."""
from __future__ import annotations
import hashlib
import time


def build_mock_response(path: str, method: str, status: int = 200,
                          body: dict | None = None, delay_ms: int = 0) -> dict:
    resp_id = hashlib.sha256(f"{method}:{path}:{time.time()}".encode()).hexdigest()[:8]
    return {"id": resp_id, "path": path, "method": method.upper(),
            "status": status, "body": body or {}, "delay_ms": delay_ms,
            "headers": {"content-type": "application/json", "x-mock": "true"}}


def mock_collection(mocks: list[dict]) -> dict:
    by_method: dict[str, int] = {}
    for m in mocks:
        by_method[m["method"]] = by_method.get(m["method"], 0) + 1
    return {"total": len(mocks), "by_method": by_method,
            "paths": sorted({m["path"] for m in mocks})}
