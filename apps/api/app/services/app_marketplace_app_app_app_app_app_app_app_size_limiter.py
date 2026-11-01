"""Request size limiter — enforce request/response size limits."""
from __future__ import annotations


def check_request_size(body_bytes: int, max_bytes: int = 1048576) -> dict:
    allowed = body_bytes <= max_bytes
    pct = round(body_bytes / max_bytes * 100, 1)
    return {"allowed": allowed, "body_bytes": body_bytes,
            "max_bytes": max_bytes, "pct_of_limit": pct,
            "human_size": _human_size(body_bytes),
            "human_limit": _human_size(max_bytes)}


def _human_size(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{round(b, 1)}{unit}"
        b /= 1024
    return f"{round(b, 1)}TB"


def batch_check(requests: list[dict], max_bytes: int = 1048576) -> dict:
    results = []
    rejected = 0
    for r in requests:
        check = check_request_size(r["size_bytes"], max_bytes)
        if not check["allowed"]:
            rejected += 1
        results.append({"path": r.get("path", ""), **check})
    return {"total": len(requests), "rejected": rejected,
            "accepted": len(requests) - rejected}
