"""Request replay tool — capture and replay API requests."""
from __future__ import annotations
import hashlib
import time

_captures: list[dict] = []


def capture_request(method: str, path: str, headers: dict, body: str = "") -> dict:
    req_id = hashlib.sha256(f"{method}:{path}:{time.time()}".encode()).hexdigest()[:10]
    entry = {"id": req_id, "method": method.upper(), "path": path,
             "headers": {k: v for k, v in headers.items() if k.lower() not in ("authorization", "cookie")},
             "body": body, "captured_at": time.time()}
    _captures.append(entry)
    return entry


def replay_request(req_id: str) -> dict:
    for c in _captures:
        if c["id"] == req_id:
            return {"replayed": True, "method": c["method"], "path": c["path"],
                    "body_length": len(c["body"]), "original_time": c["captured_at"]}
    return {"replayed": False, "error": "not_found"}


def list_captures(limit: int = 20) -> list[dict]:
    return [{"id": c["id"], "method": c["method"], "path": c["path"]}
            for c in reversed(_captures[-limit:])]


def clear_captures() -> None:
    _captures.clear()
