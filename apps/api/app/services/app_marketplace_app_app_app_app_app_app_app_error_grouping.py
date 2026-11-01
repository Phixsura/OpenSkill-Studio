"""Error grouping engine — aggregate errors into groups by stack trace fingerprint."""
from __future__ import annotations
import hashlib


def group_errors(errors: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    for e in errors:
        stack = e.get("stack_trace", "")
        message = e.get("message", "")
        fingerprint = hashlib.sha256(f"{message}:{stack[:200]}".encode()).hexdigest()[:12]
        if fingerprint not in groups:
            groups[fingerprint] = {
                "fingerprint": fingerprint, "message": message,
                "first_seen": e.get("timestamp", ""), "last_seen": e.get("timestamp", ""),
                "count": 0, "sample_stack": stack[:500],
                "affected_users": set(),
            }
        g = groups[fingerprint]
        g["count"] += 1
        g["last_seen"] = e.get("timestamp", g["last_seen"])
        if e.get("user_id"):
            g["affected_users"].add(e["user_id"])
    result = []
    for g in sorted(groups.values(), key=lambda x: -x["count"]):
        result.append({**g, "affected_users": len(g["affected_users"])})
    return {"groups": result, "total_errors": len(errors),
            "unique_groups": len(result),
            "top_error": result[0]["message"] if result else None}
