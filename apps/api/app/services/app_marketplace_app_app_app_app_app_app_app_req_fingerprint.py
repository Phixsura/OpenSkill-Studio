"""Request fingerprinter — fingerprint requests for dedup and analytics."""
from __future__ import annotations
import hashlib


def fingerprint(method: str, path: str, body: str = "", headers: dict | None = None) -> dict:
    content = f"{method}:{path}:{body}"
    fp = hashlib.sha256(content.encode()).hexdigest()[:16]
    return {"fingerprint": fp, "method": method, "path": path}


def group_by_fingerprint(requests: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for r in requests:
        fp = fingerprint(r.get("method", "GET"), r.get("path", "/"), r.get("body", ""))
        key = fp["fingerprint"]
        groups.setdefault(key, []).append(r)
    unique = len(groups)
    duplicates = sum(1 for g in groups.values() if len(g) > 1)
    return {"unique_fingerprints": unique, "duplicate_groups": duplicates,
            "total_requests": len(requests),
            "dedup_savings_pct": round((1 - unique / max(len(requests), 1)) * 100, 1)}
