"""API mock server — define mock responses for API testing."""
from __future__ import annotations
import html
import json


_mocks: dict[str, dict] = {}


def register_mock(method: str, path: str, status: int = 200,
                  body: dict | None = None, delay_ms: int = 0) -> dict:
    key = f"{method.upper()}:{path}"
    _mocks[key] = {"method": method.upper(), "path": path, "status": status,
                    "body": body or {}, "delay_ms": delay_ms, "hit_count": 0}
    return {"registered": True, "key": key}


def match_mock(method: str, path: str) -> dict:
    key = f"{method.upper()}:{path}"
    mock = _mocks.get(key)
    if not mock:
        return {"matched": False, "status": 404, "body": {"error": "no mock defined"}}
    mock["hit_count"] += 1
    return {"matched": True, "status": mock["status"], "body": mock["body"],
            "delay_ms": mock["delay_ms"], "hit_count": mock["hit_count"]}


def mock_stats() -> dict:
    total_hits = sum(m["hit_count"] for m in _mocks.values())
    return {"total_mocks": len(_mocks), "total_hits": total_hits,
            "mocks": [{**m} for m in _mocks.values()]}


def clear_mocks() -> None:
    _mocks.clear()
