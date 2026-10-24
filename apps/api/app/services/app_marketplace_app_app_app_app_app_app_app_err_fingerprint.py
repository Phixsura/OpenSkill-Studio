"""Error fingerprinting — deduplicate errors by signature."""
from __future__ import annotations
import hashlib


def fingerprint_error(error_type: str, message: str, stack_top: str = "") -> str:
    normalized = f"{error_type}:{stack_top or message[:100]}"
    return hashlib.sha256(normalized.encode()).hexdigest()[:12]


def group_errors(errors: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    for e in errors:
        fp = fingerprint_error(e.get("type", ""), e.get("message", ""), e.get("stack_top", ""))
        if fp not in groups:
            groups[fp] = {"fingerprint": fp, "type": e.get("type", ""),
                          "message": e.get("message", ""), "count": 0, "first_seen": e.get("timestamp", 0)}
        groups[fp]["count"] += 1
        groups[fp]["last_seen"] = e.get("timestamp", 0)
    sorted_groups = sorted(groups.values(), key=lambda g: -g["count"])
    return {"groups": sorted_groups, "unique_errors": len(groups),
            "total_occurrences": len(errors),
            "dedup_ratio": round(len(errors) / max(len(groups), 1), 1)}
